import os

import cachetools
from fastapi import APIRouter, Header, HTTPException, Form, Security

import shutil

from fastapi.security import APIKeyHeader
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

## Use In-Memory Ram
user_model_cache = cachetools.LRUCache(maxsize=2)
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
n_gpu_layers = 40  # Change this value based on your model and your GPU VRAM pool.
n_batch = 512

llm = LlamaCpp(
    model_path=Param.LLM_MODEL_PATH,
    max_new_tokens=Param.LLM_MAX_NEW_TOKENS,
    temperature= Param.LLM_TEMPERATURE,
    top_k= Param.TOP_K,
    top_p= Param.TOP_P,
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    batch_size= Param.BATCH_SIZE,
    context_length= Param.LLM_CONTEXT_LENGTH,
    callback_manager=callback_manager,
    n_ctx=4000,
    verbose=True, # Verbose is required to pass to the callback manager
    )

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
    return {"status": "healthy"}


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
    auth = decodeJWT(authorization)
    if auth["valid"]:
        try:
            if (data.config.items() == {
                "max_new_tokens": Param.LLM_MAX_NEW_TOKENS,
                "temperature": Param.LLM_TEMPERATURE,
                "top_k": Param.TOP_K,
                "top_p": Param.TOP_P,
                "batch_size": Param.BATCH_SIZE

            }.items()):
                pass
            else:
                exist = ''
                for i in user_model_cache.keys():
                    if data.config.items() == user_model_cache[i]['config'].items():
                        exist = i
                        print('Exist Model in Cache')

                if exist == '':
                    data.config['context_length']=Param.LLM_CONTEXT_LENGTH
                    custom_llm = LlamaCpp(
                        model_path=Param.LLM_MODEL_PATH,
                        max_new_tokens=data.config['max_new_tokens']if data.config['max_new_tokens'] else Param.LLM_MAX_NEW_TOKENS,
                        temperature=data.config[
                            'temperature'] if 'temperature' in data.config else Param.LLM_TEMPERATURE,
                        top_k=data.config['top_k'] if 'top_k' in data.config else Param.TOP_K,
                        top_p=data.config['top_p'] if 'top_p' in data.config else Param.TOP_P,
                        n_gpu_layers=n_gpu_layers,
                        n_batch=n_batch,
                        batch_size=data.config['batch_size'] if 'batch_size' in data.config else Param.BATCH_SIZE,
                        context_length=data.config[
                            'context_length'] if 'context_length' in data.config else Param.LLM_CONTEXT_LENGTH,
                        callback_manager=callback_manager,
                        n_ctx=4000,
                        verbose=True,  # Verbose is required to pass to the callback manager
                    )

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
        file: List[UploadFile] = Form(...), extension: List[str] = Form(...),
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
    auth = decodeJWT(authorization)
    if auth["valid"]:
        user_folder = Param.EMBEDDING_MODEL_PATH + auth["data"]["username"] + "/"
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)
        else:
            os.makedirs(user_folder)
        file_list=[]
        for infile in file:
            file_location = f"{Param.TEMP_SAVE_PATH}/{infile.filename}"
            with open(file_location, "wb+") as file_object:
                file_object.write(infile.file.read())
                file_list.append(file_location)

        embedding = EmbeddingPipeline(file_list, auth["data"]["username"],extension)
        embedding.save_db_local()

        for address in file_list:
            if os.path.isfile(address):
                os.remove(address)
        return APIResponse(status="success", message="Embedding Created Success")
    else:
        return HTTPException(401, detail="Unauthorised")


def retrieve_model(data, username):
    print(user_model_cache.keys())
    if data.use_default == 1:
        llms = llm
        return llms
    else:
        if (username in user_model_cache.keys()):
            print('Exist Model in Cache')

            return user_model_cache[username]['model']
        else:

            for i in user_model_cache.keys():
                if data.config.items() == user_model_cache[i]['config'].items():
                    print('Exist Model in Cache')
                    llms = user_model_cache[i]['model']
                    return llms

            data.config['context_length']=Param.LLM_CONTEXT_LENGTH
            custom_llm = LlamaCpp(
                model_path=Param.LLM_MODEL_PATH,
                max_new_tokens=data.config['max_new_tokens'] if data.config[
                    'max_new_tokens'] else Param.LLM_MAX_NEW_TOKENS,
                temperature=data.config[
                    'temperature'] if 'temperature' in data.config else Param.LLM_TEMPERATURE,
                top_k=data.config['top_k'] if 'top_k' in data.config else Param.TOP_K,
                top_p=data.config['top_p'] if 'top_p' in data.config else Param.TOP_P,
                n_gpu_layers=n_gpu_layers,
                n_batch=n_batch,
                batch_size=data.config['batch_size'] if 'batch_size' in data.config else Param.BATCH_SIZE,
                context_length=data.config[
                    'context_length'] if 'context_length' in data.config else Param.LLM_CONTEXT_LENGTH,
                callback_manager=callback_manager,
                n_ctx=4000,
                verbose=True,  # Verbose is required to pass to the callback manager
            )
            user_model_cache[username] = {'model': custom_llm, 'config': data.config}
            print('Created New Model in Cache')
            return user_model_cache[username]['model']


@router.post("/predict")
@limiter.limit("5/second")
def predict(
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
    auth = decodeJWT(authorization)
    if auth["valid"]:
        retriever = load_embedding(
            Param.EMBEDDING_SAVE_PATH + auth["data"]["username"] + "/"
        )
        llms = retrieve_model(data, auth["data"]["username"])
        chain = ConversationalRetrievalChain.from_llm(
            llm=llms, retriever=retriever.as_retriever(search_type="similarity_score_threshold", search_kwargs={'k': (data.conversation_config['k'] if data.conversation_config['k'] else Param.SELECT_INDEX), 'fetch_k': (data.conversation_config['fetch_k'] if data.conversation_config['fetch_k'] else Param.FETCH_INDEX),"score_threshold": .1}),verbose=True
        )
        result = LLM(chain, llms, retriever).predict(data.query,data.chat_history[-3:] if len(data.chat_history)>3 else data.chat_history,data.conversation_config['bot_context_setting'])

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
    auth = decodeJWT(authorization)
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
api_keys=['TESTKEY123']
def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header in api_keys:
        return api_key_header
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API Key",
    )



@router.post("/create_embeddingLB")
def create_embedding(
        request: Request,
        response: Response,
        file: List[UploadFile] = Form(...), extension: List[str] = Form(...),
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

    user_folder = Param.EMBEDDING_MODEL_PATH + api_key + "/"
    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)
    else:
        os.makedirs(user_folder)
    file_list=[]
    for infile in file:
        file_location = f"{Param.TEMP_SAVE_PATH}/{infile.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(infile.file.read())
            file_list.append(file_location)

    embedding = EmbeddingPipeline(file_list, api_key,extension)
    embedding.save_db_local()

    for address in file_list:
        if os.path.isfile(address):
            os.remove(address)
    return APIResponse(status="success", message="Embedding Created Success")


@router.post("/predictLB")
def predict(
        request: Request,
        response: Response,
        data: PredictionRequest,
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

    retriever = load_embedding(
        Param.EMBEDDING_SAVE_PATH + api_key + "/"
    )
    llms = retrieve_model(data, api_key)
    chain = ConversationalRetrievalChain.from_llm(
        llm=llms, retriever=retriever.as_retriever(search_type="mmr", search_kwargs={'k': (data.conversation_config['k'] if data.conversation_config['k'] else Param.SELECT_INDEX), 'fetch_k': (data.conversation_config['fetch_k'] if data.conversation_config['fetch_k'] else Param.FETCH_INDEX)}),verbose=True
    )
    result = LLM(chain, llms, retriever).predict(data.query, data.chat_history,data.conversation_config['bot_context_setting'])

    return APIResponse(status="success", message=result)
