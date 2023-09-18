from fastapi import FastAPI
import uvicorn
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import CTransformers

from router.v1 import api as v1route
from core.settings import Param



app = FastAPI()

app.include_router(v1route.v1_router, prefix="/v1")




if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

