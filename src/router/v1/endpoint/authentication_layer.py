import math

from fastapi import APIRouter, HTTPException
from ray import serve

from core.schema.login_transaction import Login, LoginResponse
import bcrypt

from core.settings import Param

from core.controller.authentication_layer.jwt import signJWT
from core.limiter import limiter
from starlette.requests import Request
from starlette.responses import Response

router = APIRouter()


@serve.deployment(ray_actor_options={"num_cpus": Param.NUM_CPU*(1-Param.DISTRIBUTE_RATIO) if Param.NUM_CPU<1 else math.floor(Param.NUM_CPU*(1-Param.DISTRIBUTE_RATIO))},
                   autoscaling_config={
                       "target_num_ongoing_requests_per_replica": 10,
                       "min_replicas": 1,
                       "initial_replicas": 1,
                       "max_replicas": 200,
                   },)
@serve.ingress(router)
class AuthAPI:
    @router.post("/login", response_model=LoginResponse)
    def login_user(self, request: Request, response: Response, data: Login):
        """
        The login_user function is used to validate a user's credentials.
            It takes in the username and password from the request body, then compares it with the stored hash of that user's
            password. If they match, then we return a LoginResponse object with status &quot;success&quot;. Otherwise, we return an object
            with status &quot;fail&quot;.

        Args:
            data: Login: Pass the data from the request body into this function

        Returns:
            A loginresponse object"""
        with open(Param.AUTH_HASH_PASS_FILE, "r") as f:
            lines = f.readlines()
            for line in lines:
                stored_username, stored_hash = line.strip().split(":")
                if stored_username == data.username:
                    return self.validate_password(data.username, stored_hash, data.password)
        return LoginResponse(status="fail")

    def validate_password(self, username: str, stored_hash: str, provided_password: str):
        """Check if a provided password matches the stored hash."""
        result = bcrypt.checkpw(
            provided_password.encode("utf-8"), stored_hash.encode("utf-8")
        )
        if result:
            return LoginResponse(
                status="success", username=username, token=signJWT(username)
            )

        else:
            return LoginResponse(status="fail")

    @router.post("/register", response_model=LoginResponse)
    def register_user(self, request: Request, response: Response, data: Login):
        """
        The register_user function takes in a username and password, hashes the password,
        and stores it in a file. If the user already exists, an error is thrown.

        Args:
            data: Login: Pass in the data from the request body

        Returns:
            A loginresponse object with a status of success"""
        with open(Param.AUTH_HASH_PASS_FILE, "r") as f:
            lines = f.readlines()
            for line in lines:
                stored_username, stored_hash = line.strip().split(":")
                if stored_username == data.username:
                    raise HTTPException(status_code=422, detail="Duplicate User")
        hashed_passwords = {data.username: self.hash_password(data.password)}
        with open(Param.AUTH_HASH_PASS_FILE, "a") as f:
            for user, hashed_pw in hashed_passwords.items():
                f.write(f"{user}:{hashed_pw}\n")
                return LoginResponse(status="success", username=user)
        return LoginResponse(status="fail")

    def hash_password(self, password: str) -> str:
        """Hash a password for storing."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


