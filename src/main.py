from fastapi import FastAPI
import uvicorn

from slowapi.errors import RateLimitExceeded
from core.settings import Param

from router.v1 import api as v1route
from core.limiter import limiter
from core.schema.ratelimit_response import rate_limit_custom_handler
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--port', dest='port', type=int, help='Port Number')
args = parser.parse_args()

port_set=Param.PORT_NUMBER if not args.port else args.port

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_custom_handler)

app.include_router(v1route.v1_router, prefix="/v1")


if __name__ == "__main__":
    uvicorn.run(app, host=Param.RUNNING_ADDRESS, port=port_set)
