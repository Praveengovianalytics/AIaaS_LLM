from pydantic import BaseModel

class ModelRequest(BaseModel):
    """
    Model Request Model
    """
    config: dict

class PredictionRequest(BaseModel):
    """
    Prediction Request Model
    """

    query: str
    chat_history: list
    use_default:int
