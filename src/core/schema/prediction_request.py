from pydantic import BaseModel
from fastapi import FastAPI


class PredictionRequest(BaseModel):
    query: str
    chat_history:list
