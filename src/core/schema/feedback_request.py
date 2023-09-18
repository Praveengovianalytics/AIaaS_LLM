from pydantic import BaseModel
from fastapi import FastAPI


class FeedbackRequest(BaseModel):
    chat_history:list
    user_timestamp:str
    feedback_timestamp:str
    bot_timestamp:str
    feedback_timestamp:str
    feedback:str
