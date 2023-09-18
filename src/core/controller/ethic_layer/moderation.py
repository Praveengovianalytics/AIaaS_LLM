import re
from typing import Optional

from langchain import PromptTemplate, LLMChain
from langchain.llms import BaseLLM
from langchain.schema.language_model import BaseLanguageModel


def output_moderation(
    context: str = None,
    llm: Optional[BaseLanguageModel] = None,
):
    bot_response = context

    if bot_response:
        output_moderation_template = ("model output: {bot_response} \n Is the model output "
                                      "non-harmful to any person? You should evalute it purely based on information provided to you in general like in a normal document. Answer with yes/no.")

        prompt = PromptTemplate(
            template=output_moderation_template, input_variables=["bot_response"]
        )

        output_moderation_chain = LLMChain(prompt=prompt, llm=llm)
        check =  output_moderation_chain.predict(bot_response=bot_response)
        print(check)
        check = check.lower().strip()

        if ("no" in check and 'yes' not in check):
            print('moderation check fail')
            return False
        else:

            with open('core/controller/ethic_layer/en.txt') as f:
                lines = [line.rstrip() for line in f]

            for line in lines:
                if re.search(r'\b{}\b'.format(re.escape(line)), bot_response, re.IGNORECASE):
                    print('find sensitive word'+line)
                    print(bot_response)

                    return False

            return True
def moderation_check(input:str=None,llm:Optional[BaseLLM] = None):
    check=output_moderation(input,llm)
    if check:
        return {"check":'pass','content':input}
    else:
        return {"check":'fail','content':"I'm sorry, but I can't engage in discussions or provide information on harmful or unethical topics."}