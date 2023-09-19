import os

from fastapi import APIRouter, Header, HTTPException

import shutil

from langchain.chains import ConversationalRetrievalChain

from core.controller.orchestration_layer.model import LLM
from core.schema.api_response import APIResponse
from core.schema.feedback_request import FeedbackRequest
from core.schema.prediction_request import PredictionRequest
from core.settings import Param
from core.controller.orchestration_layer.embedding_pipeline import (
    EmbeddingPipeline,
    load_embedding,
)
from langchain.llms import CTransformers
from fastapi import UploadFile
from core.controller.authentication_layer.jwt import decodeJWT
from core.limiter import limiter
from starlette.requests import Request
from starlette.responses import Response

llm = CTransformers(
    model=Param.LLM_MODEL_PATH,
    model_type=Param.LLM_MODEL_TYPE,
    max_new_tokens=Param.LLM_MAX_NEW_TOKENS,
    temperature=Param.LLM_TEMPERATURE,
)
router = APIRouter()


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


@router.post("/create_embedding")
@limiter.limit("5/second")
def create_embedding(
    request: Request,
    response: Response,
    file: UploadFile,
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

        file_location = f"{Param.TEMP_SAVE_PATH}/{file.filename}"

        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        embedding = EmbeddingPipeline(file_location, auth["data"]["username"])
        embedding.save_db_local()
        if os.path.isfile(file_location):
            os.remove(file_location)
        return APIResponse(status="success", message="Embedding Created Success")
    else:
        return HTTPException(401, detail="Unauthorised")


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
        chain = ConversationalRetrievalChain.from_llm(
            llm=llm, retriever=retriever.as_retriever()
        )
        result = LLM(chain, llm, retriever).predict(data.query, data.chat_history)

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
                f"User_Timestamp: {data.user_timestamp} | User_Input: {data.chat_history[len(data.chat_history)-2]}\n"
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
