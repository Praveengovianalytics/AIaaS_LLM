import datetime
from typing import Dict

import jwt
from core.settings import Param


def signAPIJWT(username: str, project: str, department: str, email: str, day: int) -> Dict[str, str]:
    """
    The signJWT function takes a username as an argument and returns a JWT token.
    The token is signed with the secret key defined in Param.py, and expires after 180 minutes.
    Args:
        :param username: str: Specify the username of the user that is logging in

    Returns:
        :return: A token in the form of a dictionary
    """
    if day:
        payload = {
            "username": username,
            'project': project,
            "department": department,
            "email": email,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                   + datetime.timedelta(minutes=day * 24 * 60),
        }
    else:
        payload = {
            "username": username,
            'project': project,
            "department": department,
            "email": email
        }
    token = jwt.encode(payload, Param.JWT_API_SECRET_KEY, algorithm=Param.JWT_API_ALGORITHM)

    return token


def decodeAPIJWT(token: str) -> dict:
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
            token,
            Param.JWT_API_SECRET_KEY,
            algorithms=Param.JWT_API_ALGORITHM,
        )
        return {"valid": True, "data": decoded_token, "type": 0}
    except jwt.ExpiredSignatureError:
        return {"valid": False, "data": "Your Session Has Expired", "type": 1}
    except Exception as e:
        print(str(e))
        return {"valid": False, "data": "Invalid Authentication", "type": 2}
