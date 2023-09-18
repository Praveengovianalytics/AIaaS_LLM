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
        decoded_token = jwt.decode(token.split('Bearer ')[1], Param.JWT_SECRET_KEY, algorithms=Param.JWT_ALGORITHM)
        return {'valid':True,'data':decoded_token,'type':0}
    except jwt.ExpiredSignatureError:
        return {'valid':False,'data':'Your Session Has Expired','type':1}
    except:
        return {'valid':False,'data':'Invalid Authentication','type':2}
