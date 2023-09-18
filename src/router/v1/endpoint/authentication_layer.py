from fastapi import APIRouter
from ctransformers import AutoModelForCausalLM,AutoTokenizer
import json
from core.schema.Login import Login,LoginResponse
import bcrypt

from core.settings import Param

router = APIRouter()


@router.post("/login",response_model=LoginResponse)
def login_user(data:Login):
    with open(Param.AUTH_HASH_PASS_FILE, 'r') as f:
        lines = f.readlines()
        for line in lines:
            stored_username, stored_hash = line.strip().split(":")
            if stored_username == data.username:
                return validate_password(data.username,stored_hash, data.password)
    return LoginResponse(status='fail')
def validate_password(username:str,stored_hash: str, provided_password: str) -> dict:
    """Check if a provided password matches the stored hash."""
    result=bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
    if result:
        return LoginResponse(status='success',username=username)

    else:
        return LoginResponse(status='fail')
