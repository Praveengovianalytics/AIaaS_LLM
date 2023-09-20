from pydantic import BaseModel


class PredictionRequest(BaseModel):
    """
    Prediction Request Model
    """

    query: str
    chat_history: list
