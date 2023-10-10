from fastapi import APIRouter
from ray import serve

from router.v1.endpoint import chatbot
from router.v1.endpoint import authentication_layer as authentication


class Deploy:
    def __init__(self,port,address):
        self.api_load=[chatbot.ChatbotAPI,authentication.AuthAPI]
        self.port=port
        self.address=address

    def load_api(self):
        serve.run(chatbot.ChatbotAPI.bind(),name='chat',route_prefix='/v1/chat',port=self.port,host=self.address)
        serve.run(authentication.AuthAPI.bind(),name='auth',route_prefix='/v1/auth',port=self.port,host=self.address)



