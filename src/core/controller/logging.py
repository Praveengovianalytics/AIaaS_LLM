
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

import ctypes

from llama_cpp import llama_log_set

def my_log_callback(level, message, user_data):
   logger.info(message)


log_callback = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)(my_log_callback)
llama_log_set(log_callback, ctypes.c_void_p())
