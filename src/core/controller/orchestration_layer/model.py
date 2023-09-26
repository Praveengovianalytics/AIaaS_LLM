from typing import Optional, Type

from langchain import FAISS
from langchain.chains.conversational_retrieval.base import (
    BaseConversationalRetrievalChain,
)
from langchain.schema.language_model import BaseLanguageModel
from core.controller.ethic_layer.fact_checking import fact_checking
from core.controller.ethic_layer.jailbreak import check_jailbreak

from core.controller.ethic_layer.moderation import moderation_check


class LLM:
    def __init__(
        self,
        chain: Optional[BaseConversationalRetrievalChain] = None,
        llm: Optional[Type[BaseLanguageModel]] = None,
        retriever: FAISS = None,
    ):
        """
        The __init__ function is called when the class is instantiated.
        It sets up the instance of the class, and defines what attributes it has.
        The __init__ function can take arguments, but does not have to.

        Args:
            self: Refer to the object itself
            chain: Optional[BaseConversationalRetrievalChain]: Pass in a chain that will be used to process the input
            llm: Optional[Type[BaseLanguageModel]]: Pass in the language model class
            retriever: FAISS: Pass the faiss index to the class
            : Set the chain of components that will be used to process a query

        Returns:
            The self object, which is the instance of the class
        """
        self.chain = chain
        self.llm = llm
        self.retriever = retriever


    def pre_check(self, query: str = None):
        """
        The pre_check function is used to check if the device has been jailbroken.
            It will return a boolean value of True or False depending on whether it finds any evidence of a jailbreak.

        Args:
            self: Represent the instance of the class
            query: str: Pass the query string to the check_jailbreak function

        Returns:
            A dictionary with the following keys:
        """
        result = check_jailbreak(query, self.llm)
        return result

    def post_check(self, inputs: str = None, llm: Optional[BaseLanguageModel] = None):
        """
        The post_check function takes in a string of text and returns the result of moderation_check and fact checking.
        Args:
            self: Represent the instance of the class
            inputs: str: A string containing the bot's input.
            llm: Optional[BaseLanguageModel]: Pass a language model to the post_check function

        Returns:
            A dictionary with the following keys:
        """
        check1 = fact_checking(inputs, self.retriever, self.llm)
        print(check1)
        result = moderation_check(check1["content"], llm)
        return result

    def predict(self, query: str = None, chat_history: list = None):
        """
        The predict function takes in a query and chat history, and returns an answer.
        The predict function is the main function of the bot. It takes in a user's query as well as
        the chat history between the user and bot, processes it using various functions defined above,
        and returns an answer to be displayed to the user.

        Args:
            self: Represent the instance of the class
            query: str: Pass the user's query to the bot
            chat_history: list: Store the chat history of the user

        Returns:
            A dictionary with the key &quot;answer&quot; and value as the answer

        """
        pre_require = self.pre_check(query)
        print(pre_require)
        if pre_require["check"] == "pass":
            result = self.chain(
                {
                    "question": query+" \n System: Do note that Your are a data dictionary bot. Your task is to fully answer the "
                    "user's query based on the"
                    "information provided to you."+ "You do not respond as 'User' or pretend to be 'User'. You only response once. Please ensure that your answer is clear"
                    ,
                    "chat_history": [tuple(sublist) for sublist in chat_history],
                }
            )
            print(result)
        else:
            return pre_require["content"]

        postcheck = self.post_check(result["answer"], self.llm)
        print(postcheck)

        return postcheck["content"]
