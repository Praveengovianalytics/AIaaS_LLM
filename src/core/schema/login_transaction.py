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
    username: str
    token: str


class APIKeyNewResponse(BaseModel):
    """
    Login Response Model
    """

    status: str
    api: str


class APIKEYRequest(BaseModel):
    """
    Login Response Model
    """

    email: str
    username: str
    email: str
    department: str
    project: str
    day: int
