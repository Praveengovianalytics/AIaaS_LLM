from fastapi import APIRouter
from router.v1.endpoint import chatbot
from router.v1.endpoint import authentication_layer as authentication

v1_router = APIRouter()

v1_router.include_router(chatbot.router, prefix="/chat")
v1_router.include_router(authentication.router, prefix="/auth")
