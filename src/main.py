from fastapi import FastAPI
import uvicorn
from ray import serve
from ray.serve import Application

from slowapi.errors import RateLimitExceeded
from core.settings import Param

from router.v1 import api as v1route
from core.limiter import limiter
from core.schema.ratelimit_response import rate_limit_custom_handler
import argparse

from router.v1.api import Deploy

parser = argparse.ArgumentParser()
parser.add_argument('--port', dest='port', type=int, help='Port Number')
args = parser.parse_args()

port_set = Param.PORT_NUMBER if not args.port else args.port

deployment = Deploy()
deployment.load_api()



