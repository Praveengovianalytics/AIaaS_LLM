import logging

from core.settings import Param

config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "access": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Param.LOG_PATH+Param.ENVIRONMENT+'-log.txt',
        },
        "access": {
            "formatter": "access",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": Param.LOG_PATH+Param.ENVIRONMENT+'-log.txt',
        },
        "loki":{
            "formatter": "access",
            "class": "logging_loki.LokiHandler",
            "url" : "http://127.0.0.1:3100/loki/api/v1/push",
            "version" : "1",
            "tags" : {"application": "aiaas-llm"}

        }
    },
    "loggers": {
        "uvicorn.error": {
            "level": "ERROR",
            "handlers": ["default","loki"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access","loki"],
            "propagate": False,
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["default"],
            "propagate": False,
        },
    },
}
