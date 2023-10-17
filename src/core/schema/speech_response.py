from pydantic import BaseModel

class AudioRequest(BaseModel):
    """
    Model Request Model
    """
    audio: dict


