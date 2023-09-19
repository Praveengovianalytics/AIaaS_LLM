from pydantic import BaseModel


class APIResponse(BaseModel):
    """
    API Response Model
    """

    status: str
    message: str
