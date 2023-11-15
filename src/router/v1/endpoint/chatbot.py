import datetime
import logging
import os

import cachetools
from fastapi import APIRouter, Header, HTTPException, Form, Security

import shutil

from fastapi.security import APIKeyHeader
from langchain import OpenAI
from langchain.callbacks import StreamingStdOutCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain.chains import ConversationalRetrievalChain
from typing import List

from core.controller.orchestration_layer.model import LLM
from core.schema.api_response import APIResponse
from core.schema.feedback_request import FeedbackRequest
from core.schema.prediction_request import PredictionRequest
from core.settings import Param
from core.controller.orchestration_layer.embedding_pipeline import (
    EmbeddingPipeline,
    load_embedding,
)
from fastapi import UploadFile
from core.controller.authentication_layer.jwt import decodeJWT
from core.limiter import limiter
from starlette.requests import Request
from starlette.responses import Response
from langchain.llms import LlamaCpp
from core.schema.prediction_request import ModelRequest

from core.controller.orchestration_layer.science_pipeline import DataPipeline

from core.controller.orchestration_layer.base import create_pandas_dataframe_agent

from core.controller.authentication_layer.api_jwt import decodeAPIJWT

from core.schema.prediction_request import PredictionRequestAPI

## Use In-Memory Ram

user_model_cache = cachetools.LRUCache(maxsize=1)
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
n_gpu_layers = 35  # Change this value based on your model and your GPU VRAM pool.
n_batch = 256

router = APIRouter()


@router.get("/get_configure")
@limiter.limit("5/second")
def get_configuration(request: Request, response: Response):
    """
    The get_configuration function is a simple function that returns the configuration of the Model.
        ---
        description: Returns the configuration of this API.
        responses:
          200:  # HTTP Status code 200 means &quot;OK&quot; (the request was fulfilled)
            description: The health check passed and this API is healthy!

    Returns:
        A dictionary with a key of &quot;status&quot; and a value of &quot;healthy&quot;
    """
    return {"status": "success", "config": {
        "max_new_tokens": Param.LLM_MAX_NEW_TOKENS,
        "temperature": Param.LLM_TEMPERATURE,
        "top_k": Param.TOP_K,
        "top_p": Param.TOP_P,
        "batch_size": Param.BATCH_SIZE
    }}


@router.get("/get_model")
@limiter.limit("5/second")
def get_model(request: Request, response: Response):
    """
    The get_configuration function is a simple function that returns the configuration of the Model.
        ---
        description: Returns the configuration of this API.
        responses:
          200:  # HTTP Status code 200 means &quot;OK&quot; (the request was fulfilled)
            description: The health check passed and this API is healthy!

    Returns:
        A dictionary with a key of &quot;status&quot; and a value of &quot;healthy&quot;
    """
    return {"status": "success", "general_model": list(Param.LLM_MODEL.keys()),
            'data_model': list(Param.DATA_LLM_MODEL.keys())}


@router.get("/get_configure_chat")
@limiter.limit("5/second")
def get_configuration_chat(request: Request, response: Response):
    """
    The get_configuration function is a simple function that returns the configuration of the Model.
        ---
        description: Returns the configuration of this API.
        responses:
          200:  # HTTP Status code 200 means &quot;OK&quot; (the request was fulfilled)
            description: The health check passed and this API is healthy!

    Returns:
        A dictionary with a key of &quot;status&quot; and a value of &quot;healthy&quot;
    """
    return {"status": "success", "config": {
        "fetch_k": Param.FETCH_INDEX,
        "k": Param.SELECT_INDEX,
        "bot_context_prompt": Param.SYSTEM_PROMPT

    }}


@router.get("/ping")
@limiter.limit("5/second")
def health_check(request: Request, response: Response):
    """
    The health_check function is a simple function that returns the status of the API.
        ---
        description: Returns the health of this API.
        responses:
          200:  # HTTP Status code 200 means &quot;OK&quot; (the request was fulfilled)
            description: The health check passed and this API is healthy!

    Returns:
        A dictionary with a key of &quot;status&quot; and a value of &quot;healthy&quot;
    """
    print(request.url)

    return {"status": "healthy"}


def build_model(data):
    if data.type == 'general':
        custom_llm = LlamaCpp(
            model_path=Param.LLM_MODEL[data.config['model']],
            temperature=data.config[
                'temperature'] if 'temperature' in data.config else Param.LLM_TEMPERATURE,
            top_k=data.config['top_k'] if 'top_k' in data.config else Param.TOP_K,
            top_p=data.config['top_p'] if 'top_p' in data.config else Param.TOP_P,
            n_gpu_layers=n_gpu_layers,
            n_batch=n_batch,
            seed=0,
            callback_manager=callback_manager,
            n_ctx=4000,
            verbose=True,  # Verbose is required to pass to the callback manager
        )
    else:
        custom_llm = LlamaCpp(
            model_path=Param.DATA_LLM_MODEL[data.config['model']],
            temperature=0,
            n_gpu_layers=n_gpu_layers,
            n_batch=n_batch,
            max_tokens=8000,
            callback_manager=callback_manager,
            n_ctx=4000,
            verbose=True,  # Verbose is required to pass to the callback manager
        )
    return custom_llm


@router.post("/set_model")
@limiter.limit("5/second")
def set_model(request: Request, response: Response, data: ModelRequest, authorization: str = Header(None),
              ):
    """
    The set_model function is a simple function that initialise the model for user.
        ---
        description: Returns the health of this API.
        responses:
          200:  # HTTP Status code 200 means &quot;OK&quot; (the request was fulfilled)

    Returns:
        A dictionary with a key of &quot;status&quot; and a value of &quot;healthy&quot;
    """
    auth = decodeJWT(authorization, request.url)

    if auth["valid"]:
        try:
            exist = ''
            for i in user_model_cache.keys():
                if data.config.items() == user_model_cache[i]['config'].items():
                    exist = i
                    print('Exist Model in Cache')

            if exist == '':
                data.config['context_length'] = Param.LLM_CONTEXT_LENGTH
                custom_llm = build_model(data)

                user_model_cache[auth["data"]["username"]] = {'model': custom_llm, 'config': data.config}
                print('Created New Model in Cache')

            return APIResponse(status="success", message='Model Initialisation Success')
        except Exception:
            return APIResponse(status="fail", message='Model Initialisation Failed')


@router.post("/create_embedding")
@limiter.limit("5/second")
def create_embedding(
        request: Request,
        response: Response,
        file: List[UploadFile] = Form(...), extension: List[str] = Form(...), type: str = Form(...),
        authorization: str = Header(None),
):
    """
    The create_embedding function creates a new embedding file.

    Args:

        file: File Received
        authorization: str: Get the jwt token from the header
        : Get the embedding model for a particular user

    Returns:
        A success message if the embedding is created successfully"""
    auth = decodeJWT(authorization, request.url)

    if auth["valid"]:
        user_folder = Param.EMBEDDING_SAVE_PATH + auth["data"]["username"] + "/"
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)

        os.makedirs(user_folder)
        os.makedirs(user_folder + 'data/')
        os.makedirs(user_folder + 'embedding/')

        file_list = []

        for index, infile in enumerate(file):
            file_location = f"{Param.EMBEDDING_SAVE_PATH}/{auth['data']['username']}/data/{infile.filename}.{extension[index]}"
            with open(file_location, "wb+") as file_object:
                file_object.write(infile.file.read())
                file_list.append(file_location)

        embedding = EmbeddingPipeline(file_list, auth["data"]["username"], extension)
        embedding.save_db_local()

        return APIResponse(status="success", message="Embedding Created Success")
    else:
        return HTTPException(401, detail="Unauthorised")


def retrieve_model(data, username):
    if username in user_model_cache.keys():
        if user_model_cache[username]['config'].items() == data.config.items():

            print('Exist Model in Cache')

            return user_model_cache[username]['model']
        else:
            for i in user_model_cache.keys():
                if data.config.items() == user_model_cache[i]['config'].items():
                    print('Exist Model in Cache')
                    llms = user_model_cache[i]['model']
                    return llms


    else:
        for i in user_model_cache.keys():
            if data.config.items() == user_model_cache[i]['config'].items():
                print('Exist Model in Cache')
                llms = user_model_cache[i]['model']
                return llms

    custom_llm = build_model(data)
    user_model_cache[username] = {'model': custom_llm, 'config': data.config}
    print('Created New Model in Cache')
    return user_model_cache[username]['model']


@router.post("/predict")
@limiter.limit("5/second")
async def predict(
        request: Request,
        response: Response,
        data: PredictionRequest,
        authorization: str = Header(None),
):
    """
    The predict function is the main function of this API. It takes in a query and chat history,
    and returns a response from the model. The predict function also requires an authorization header
    which contains a JWT token that has been signed by our server.

    Args:
        data: PredictionRequest: Pass the query and chat history to the predict function
        authorization: str: Pass the jwt token to the function
        : Pass the query and chat history to the model

    Returns:
        A predictions response"""
    auth = decodeJWT(authorization, request.url)

    if auth["valid"]:
        llms = retrieve_model(data, auth["data"]["username"])
        if data.type == 'general':
            retriever = load_embedding(
                Param.EMBEDDING_SAVE_PATH + auth["data"]["username"] + "/embedding/"
            )

            chain = ConversationalRetrievalChain.from_llm(
                llm=llms, retriever=retriever.as_retriever(search_type="similarity_score_threshold", search_kwargs={
                    'k': (data.conversation_config['k'] if data.conversation_config['k'] else Param.SELECT_INDEX),
                    'fetch_k': (
                        data.conversation_config['fetch_k'] if data.conversation_config[
                            'fetch_k'] else Param.FETCH_INDEX),
                    "score_threshold": .001}), verbose=True
            )
            result = LLM(chain, llms, retriever, 'general').predict(data.query, data.chat_history[-3:] if len(
                data.chat_history) > 3 else data.chat_history, data.conversation_config['bot_context_setting'], 1)
        else:
            datadf = DataPipeline(Param.EMBEDDING_SAVE_PATH + auth["data"]["username"] + "/data/")
            datadf = datadf.process()
            agent = create_pandas_dataframe_agent(llms, datadf, verbose=True, number_of_head_rows=5,
                                                  handle_parsing_errors=True,
                                                  prefix="Follow the given template for your response. Do not use the "
                                                         "sample table data provided to you, as it's incomplete and "
                                                         "can result in incorrect inferences. Use answers in the "
                                                         "Observation. You should not making any assumption about the "
                                                         "data in Thought. When crafting your response, consistently "
                                                         "designate the Action as 'python_repl_ast'. Once you've "
                                                         "reached your conclusion, sign off your response with 'Final "
                                                         "Answer: <your final answer>'.")

            result = LLM(agent, llms, None, 'data').predict(data.query)

        return APIResponse(status="success", message=result)
    else:
        return HTTPException(401, detail="Unauthorised")


@router.post("/feedback")
@limiter.limit("5/second")
def feedback(
        request: Request,
        response: Response,
        data: FeedbackRequest,
        authorization: str = Header(None),
):
    """
    The feedback function is used to log the user's feedback on a particular interaction with the bot.
    The function takes in a request object, response object and data from the request body. The data contains
    the chat history of that interaction, timestamps for each message sent by both parties and finally
    the user's feedback on that interaction.

    Args:
        data: FeedbackRequest: Receive the feedback data from the user
        authorization: str: Pass the jwt token in the header
        : Get the user's feedback

    Returns:
        A json object with the status and message"""
    auth = decodeJWT(authorization, request.url)

    if auth["valid"]:
        with open(
                Param.FEEDBACK_LOG_FILE + "feedback_" + auth["data"]["username"] + ".txt",
                "a+",
                encoding="utf-8",
        ) as log_file:
            log_file.write(
                f"User_Timestamp: {data.user_timestamp} | User_Input: {data.chat_history[len(data.chat_history) - 2]}\n"
            )
            log_file.write(
                f"Bot_Timestamp: {data.bot_timestamp} | Bot_Response: {data.chat_history[-1]}\n"
            )
            log_file.write(
                f"Feedback_Timestamp: {data.feedback_timestamp} | User_Feedback: {data.feedback}\n"
            )
            log_file.write("=" * 50 + "\n")

        return APIResponse(status="success", message="Feedback Noted")
    else:
        return HTTPException(401, detail="Unauthorised")


api_key_header = APIKeyHeader(name="X-API-Key")


def get_api_key(api_key_header: str = Security(api_key_header), request: Request = '') -> str:
    datas = decodeAPIJWT(api_key_header)
    if datas['valid']:
        logging.info(f'{datetime.datetime.now()} - {request.url}:{datas}')
        return api_key_header
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API Key",
    )


@router.post("/create_embeddingLB")
def create_embedding(
        request: Request,
        response: Response,
        file: List[UploadFile] = Form(...), extension: List[str] = Form(...), type: str = Form(...),
        api_key: str = Security(get_api_key),
):
    """
    The create_embedding function creates a new embedding file.

    Args:

        file: File Received
        authorization: str: Get the jwt token from the header
        : Get the embedding model for a particular user

    Returns:
        A success message if the embedding is created successfully"""
    print(api_key)

    user_folder = Param.EMBEDDING_SAVE_PATH + api_key + "/"
    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)

    os.makedirs(user_folder)
    os.makedirs(user_folder + 'data/')
    os.makedirs(user_folder + 'embedding/')

    file_list = []

    for index, infile in enumerate(file):
        file_location = f"{Param.EMBEDDING_SAVE_PATH}/{api_key}/data/{infile.filename}.{extension[index]}"
        with open(file_location, "wb+") as file_object:
            file_object.write(infile.file.read())
            file_list.append(file_location)

    embedding = EmbeddingPipeline(file_list, api_key, extension)
    embedding.save_db_local()

    return APIResponse(status="success", message="Embedding Created Success")


import os

os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
from langchain.llms import AzureOpenAI


@router.post("/predictLB")
def predict(
        request: Request,
        response: Response,
        data: PredictionRequestAPI,
        api_key: str = Security(get_api_key),
):
    """
    The predict function is the main function of this API. It takes in a query and chat history,
    and returns a response from the model. The predict function also requires an authorization header
    which contains a JWT token that has been signed by our server.

    Args:
        data: PredictionRequest: Pass the query and chat history to the predict function
        authorization: str: Pass the jwt token to the function
        : Pass the query and chat history to the model

    Returns:
        A predictions response"""

    if data.config['model'] == 'openai':
        os.environ["OPENAI_API_KEY"] = data.config['api_key']
        os.environ["OPENAI_API_BASE"] = data.config['api_address']
        llms = AzureOpenAI(model_name='gpt-3.5-turbo-16k', engine='gpt-35-turbo-16k-0613-vanilla',temperature=0)
    else:
        llms = retrieve_model(data, api_key)
        print(llms)

    if data.type == 'general':
        if data.use_file:
            retriever = load_embedding(
                Param.EMBEDDING_SAVE_PATH + api_key + "/embedding/"
            )

            chain = ConversationalRetrievalChain.from_llm(
                llm=llms, retriever=retriever.as_retriever(search_type="similarity_score_threshold", search_kwargs={
                    'k': (data.conversation_config['k'] if data.conversation_config['k'] else Param.SELECT_INDEX),
                    'fetch_k': (
                        data.conversation_config['fetch_k'] if data.conversation_config[
                            'fetch_k'] else Param.FETCH_INDEX),
                    "score_threshold": .001}), verbose=True
            )
            result = LLM(chain, llms, retriever, 'general').predict(data.query, data.chat_history[-3:] if len(
                data.chat_history) > 3 else data.chat_history, data.conversation_config['bot_context_setting'], 1)
        else:
            retriever = None
            result = LLM(llms, llms, retriever, 'general').predict(data.query, data.chat_history[-10:] if len(
                data.chat_history) > 10 else data.chat_history, data.conversation_config['bot_context_setting'], 0)
    else:
        datadf = DataPipeline(Param.EMBEDDING_SAVE_PATH + api_key + "/data/")
        datadf = datadf.process()
        agent = create_pandas_dataframe_agent(llms, datadf, verbose=True, number_of_head_rows=5,
                                              handle_parsing_errors=True,
                                              prefix="Follow the given template for your response. Do not use the "
                                                     "sample table data provided to you, as it's incomplete and "
                                                     "can result in incorrect inferences. Use answers in the "
                                                     "Observation. You should not making any assumption about the "
                                                     "data in Thought. When crafting your response, consistently "
                                                     "designate the Action as 'python_repl_ast'. Once you've "
                                                     "reached your conclusion, sign off your response with 'Final "
                                                     "Answer: <your final answer>'.")

        result = LLM(agent, llms, None, 'data').predict(data.query)

    return APIResponse(status="success", message=result)
