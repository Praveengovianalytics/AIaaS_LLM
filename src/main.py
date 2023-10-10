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
parser.add_argument('--address', dest='address', type=str, help='Host')

args = parser.parse_args()

port_set = 8000 if not args.port else args.port
address_set = "0.0.0.0" if not args.address else args.address

deployment = Deploy(port=port_set,address=address_set)
deployment.load_api()



