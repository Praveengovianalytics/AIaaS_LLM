from pydantic import BaseModel

class ModelRequest(BaseModel):
    """
    Model Request Model
    """
    config: dict
    type: str

class PredictionRequest(BaseModel):
    """
    Prediction Request Model
    """

    query: str
    type:str
    chat_history: list
    use_default:int
    config:dict
    conversation_config:dict

class PredictionRequestAPI(BaseModel):
    """
    Prediction Request Model
    """

    query: str
    type:str
    chat_history: list
    use_default:int
    config:dict
    conversation_config:dict
    use_file:int
