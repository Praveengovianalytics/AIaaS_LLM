from fastapi import FastAPI
import uvicorn

from slowapi.errors import RateLimitExceeded

from router.v1 import api as v1route
from core.limiter import limiter
from core.schema.ratelimit_response import rate_limit_custom_handler

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_custom_handler)

app.include_router(v1route.v1_router, prefix="/v1")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
