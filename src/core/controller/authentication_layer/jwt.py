import datetime
import time
from typing import Dict

import jwt
from src.core.settings import Param


def signJWT(username: str) -> Dict[str, str]:
    payload = {
        "username": username,
        "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=180)
    }
    token = jwt.encode(payload, Param.JWT_SECRET_KEY, algorithm=Param.JWT_ALGORITHM)

    return token


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, Param.JWT_SECRET_KEY, algorithms=Param.JWT_ALGORITHM)
        return {'valid':True,'data':decoded_token}
    except jwt.ExpiredSignatureError:
        return {'valid':False,'data':'Your Session Has Expired'}
    except:
        return {'valid':False,'data':'Unknown Error'}
