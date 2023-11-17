import datetime
import logging

from fastapi import FastAPI
import uvicorn
from prometheus_fastapi_instrumentator import Instrumentator

from slowapi.errors import RateLimitExceeded
from core.settings import Param

from router.v1 import api as v1route
from core.limiter import limiter
from core.schema.ratelimit_response import rate_limit_custom_handler
import argparse

from logs import log_config
import logging
import logging_loki

parser = argparse.ArgumentParser()
parser.add_argument('--port', dest='port', type=int, help='Port Number')
args = parser.parse_args()

port_set=Param.PORT_NUMBER if not args.port else args.port
handler = logging_loki.LokiHandler(
   url="http://127.0.0.1:3100/loki/api/v1/push",
   version="1",
)
logging.basicConfig(filename=Param.LOG_PATH+Param.ENVIRONMENT+'-log.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.info('='*20)
logger.info(f' {datetime.datetime.now()} -BTO AIS Backend Service')
logger.info(f' {datetime.datetime.now()} -Environment: {Param.ENVIRONMENT}')
logger.info(f' {datetime.datetime.now()} -Version: {Param.VERSION_INFO}')
logger.info('='*20)
app = FastAPI()
app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, rate_limit_custom_handler)

app.include_router(v1route.v1_router, prefix="/v1")

instrumentator = Instrumentator().instrument(app)

@app.on_event("startup")
async def _startup():
    instrumentator.expose(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host=Param.RUNNING_ADDRESS, port=port_set,log_config=log_config.config,workers=2)

