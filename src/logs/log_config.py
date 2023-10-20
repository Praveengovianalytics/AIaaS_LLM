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
    },
    "loggers": {
        "uvicorn.error": {
            "level": "ERROR",
            "handlers": ["default"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "INFO",
            "handlers": ["access"],
            "propagate": False,
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["default"],
            "propagate": False,
        },
    },
}
