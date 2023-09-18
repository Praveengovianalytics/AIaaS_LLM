from typing import Optional, Type

from langchain import FAISS
from langchain.chains.conversational_retrieval.base import BaseConversationalRetrievalChain
from langchain.schema import BaseRetriever
from langchain.schema.language_model import BaseLanguageModel
from nemoguardrails.llm.providers import register_llm_provider
from langchain.llms import CTransformers, BaseLLM
from langchain.chains import ConversationalRetrievalChain
import sys
from nemoguardrails.llm.taskmanager import LLMTaskManager
from nemoguardrails.rails.llm.config import Model, RailsConfig

from core.controller.ethic_layer.fact_checking import fact_checking
from core.controller.ethic_layer.jailbreak import check_jailbreak
import sys

from core.controller.ethic_layer.moderation import moderation_check


class LLM():

    def __init__(self, chain:Optional[BaseConversationalRetrievalChain] = None, llm:Optional[Type[BaseLanguageModel]] = None, retriever:FAISS=None):
        self.chain = chain
        self.llm = llm
        self.retriever = retriever
        register_llm_provider("custom_llm", llm)
        model_config = Model(type="main", engine='customllm')
        rails_config = RailsConfig(models=[model_config])
        self.llm_task_manager = LLMTaskManager(rails_config)

    def pre_check(self, query: str = None):
        result = check_jailbreak(query, self.llm)
        return result

    def post_check(self, inputs: str = None, llm: Optional[BaseLanguageModel] = None):
        check1= fact_checking(inputs, self.retriever, self.llm)
        print(check1)
        result = moderation_check(check1['content'], llm)
        return result

    def predict(self, query: str = None, chat_history: list = None):
        pre_require = self.pre_check(query)
        print(pre_require)
        if pre_require['check'] == 'pass':
            result = self.chain({
                                    "question": "Your are a data dictionary bot. Your task is to fully answer the "
                                                "user's query based on the"
                                                "information provided to you. The user's query will be based on the "
                                                "data provided to you."
                                                "Your response should "
                                                "be comprehensive, evident and provide all the necessary information "
                                                "using the data given to you to"
                                                "explain and address the user query.You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'. Please ensure that your answer "
                                                "is clear,"
                                                "concise, and accurate, using the provided data and attributes to provide a "
                                                "complete and informative response. Just mention everything you know "
                                                "about the query from the data provided. "
                                                "\n "
                                                " User query:" + query,
                                    "chat_history": chat_history})
            print(result)
        else:
            return pre_require['content']

        postcheck = self.post_check(result['answer'], self.llm)
        print(postcheck)

        return postcheck['content']
