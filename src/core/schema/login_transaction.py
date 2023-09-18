from pydantic import BaseModel
from fastapi import FastAPI


class Login(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    status: str
    username: str | None = None
    token: str | None=None
