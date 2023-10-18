import pandas as pd
from langchain import LlamaCpp
from langchain.agents import create_pandas_dataframe_agent, AgentType
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager

from core.settings import Param
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

custom_llm = LlamaCpp(
    model_path='../models/codellama-13b-instruct.Q4_K_M.gguf',
    max_new_tokens= Param.LLM_MAX_NEW_TOKENS,
    temperature=0,
    top_p=1,
    n_gpu_layers=40,
    n_batch=256,
    batch_size=Param.BATCH_SIZE,
    context_length=Param.LLM_CONTEXT_LENGTH,
    callback_manager=callback_manager,
    n_ctx=4000,
    verbose=True,  # Verbose is required to pass to the callback manager
)
df = pd.read_csv("/home/praveengovi_nlp/AIaaS_Projects/AIaas_LLM/AIaaS_LLM/data/raw/01Aug2023.csv")

agent=create_pandas_dataframe_agent(
    custom_llm,
    df,
    prefix="Set the Action to everything inside the single quote with no addition or removal or anything:'python_repl_ast' ",
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)
agent.run("How many foreign key are there for the account entity? ")

