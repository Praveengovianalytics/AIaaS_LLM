from fastapi import FastAPI
import uvicorn
from router.v1 import api as v1route

app = FastAPI()

app.include_router(v1route.v1_router, prefix="/v1")




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

