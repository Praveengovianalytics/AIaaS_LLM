from pydantic import BaseModel


class Login(BaseModel):
    """
    Login Request Model
    """

    username: str
    password: str


class LoginResponse(BaseModel):
    """
    Login Response Model
    """

    status: str
    username: str | None = None
    token: str | None = None
