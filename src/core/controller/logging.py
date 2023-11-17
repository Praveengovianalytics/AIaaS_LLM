
import logging
import logging_loki

from core.settings import Param

handler = logging_loki.LokiHandler(
   url="http://127.0.0.1:3100/loki/api/v1/push",
   version="1",
    tags={"application": "aiaas-llm"},
)
logging.basicConfig(filename=Param.LOG_PATH+Param.ENVIRONMENT+'-log.txt',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(handler)