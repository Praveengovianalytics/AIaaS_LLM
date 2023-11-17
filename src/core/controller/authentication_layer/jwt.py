import datetime
import logging
from typing import Dict

import jwt
from core.settings import Param

from src.main import logger


def signJWT(username: str,request_url) -> Dict[str, str]:
    """
    The signJWT function takes a username as an argument and returns a JWT token.
    The token is signed with the secret key defined in Param.py, and expires after 180 minutes.
    Args:
        :param username: str: Specify the username of the user that is logging in

    Returns:
        :return: A token in the form of a dictionary
    """
    payload = {
        "username": username,
        "exp": datetime.datetime.now(tz=datetime.timezone.utc)
        + datetime.timedelta(minutes=180),
    }
    logger.info(f'{datetime.datetime.now()} - {username}: {request_url} ')
    token = jwt.encode(payload, Param.JWT_SECRET_KEY, algorithm=Param.JWT_ALGORITHM)

    return token


def decodeJWT(token: str,url ) -> dict:
    """
The decodeJWT function takes in a JWT token and returns the decoded payload.
If the token is invalid, it will return an error message.

Args:
    token: str: Pass in the token that is being decoded

Returns:
    A dictionary with three keys:

\
"""
    try:
        decoded_token = jwt.decode(
            token.split("Bearer ")[1],
            Param.JWT_SECRET_KEY,
            algorithms=Param.JWT_ALGORITHM,
        )
        logger.info(f'{datetime.datetime.now()} - {url}:{decoded_token}')
        return {"valid": True, "data": decoded_token, "type": 0}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "data": "Your Session Has Expired", "type": 1}
    except Exception as e:
        print(str(e))
        return {"valid": False, "data": "Invalid Authentication", "type": 2}
