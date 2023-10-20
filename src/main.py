import datetime
import logging

from fastapi import FastAPI
import uvicorn

from slowapi.errors import RateLimitExceeded
from core.settings import Param

from router.v1 import api as v1route
from core.limiter import limiter
from core.schema.ratelimit_response import rate_limit_custom_handler
import argparse

from logs import log_config

parser = argparse.ArgumentParser()
parser.add_argument('--port', dest='port', type=int, help='Port Number')
args = parser.parse_args()

port_set=Param.PORT_NUMBER if not args.port else args.port

logging.basicConfig(filename=Param.LOG_PATH+Param.ENVIRONMENT+'-log.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.info('='*20)
logging.info(f' {datetime.datetime.now()} -BTO AIS Backend Service')
logging.info(f' {datetime.datetime.now()} -Environment: {Param.ENVIRONMENT}')
logging.info(f' {datetime.datetime.now()} -Version: {Param.VERSION_INFO}')
logger.info('='*20)
app = FastAPI()
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, rate_limit_custom_handler)

app.include_router(v1route.v1_router, prefix="/v1")


if __name__ == "__main__":
    uvicorn.run(app, host=Param.RUNNING_ADDRESS, port=port_set,log_config=log_config.config,)

