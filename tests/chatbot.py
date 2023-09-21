import pytest
from fastapi.testclient import TestClient
from router.v1.endpoint.chatbot import router  # Import your FastAPI router
from core.schema.api_response import APIResponse
from core.schema.feedback_request import FeedbackRequest
from core.schema.prediction_request import PredictionRequest
from core.settings import Param
from core.controller.authentication_layer.jwt import decodeJWT, signJWT
from starlette.requests import Request
from starlette.responses import Response
import os

# Create a TestClient for the FastAPI app
client = TestClient(router)

@pytest.fixture(scope="module")
def test_data():
    return {
        "query": "Test query",
        "chat_history": ["User: Hi", "Bot: Hello", "User: Test query"],
        "user_timestamp": "2023-09-21T12:00:00Z",
        "bot_timestamp": "2023-09-21T12:01:00Z",
        "feedback_timestamp": "2023-09-21T12:02:00Z",
        "feedback": "Positive",
    }

def test_get_configuration():
    response = client.get("/get_configure")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "config" in response.json()

def test_health_check():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.parametrize("testlist", [
    # Validate Testing
    {'config': {
        "max_new_tokens": Param.LLM_MAX_NEW_TOKENS,
        "temperature": Param.LLM_TEMPERATURE,
        "top_k": Param.TOP_K,
        "top_p": Param.TOP_P,
        "batch_size": Param.BATCH_SIZE

    }},

    {'config': {
        "max_new_tokens": Param.LLM_MAX_NEW_TOKENS,
        "temperature": Param.LLM_TEMPERATURE - 0.1,
        "top_k": Param.TOP_K,
        "top_p": Param.TOP_P,
        "batch_size": Param.BATCH_SIZE + 16

    }},
    {'config': {
        "max_new_tokens": Param.LLM_MAX_NEW_TOKENS,
        "temperature": Param.LLM_TEMPERATURE - 0.1,
        "top_k": Param.TOP_K,
        "top_p": Param.TOP_P,
        "batch_size": Param.BATCH_SIZE + 16

    }},
    { 'config': {
        "max_new_tokens": Param.LLM_MAX_NEW_TOKENS,
        "temperature": Param.LLM_TEMPERATURE - 0.2,
        "top_k": Param.TOP_K,
        "top_p": Param.TOP_P,
        "batch_size": Param.BATCH_SIZE + 32

    }},

])
def test_set_model(test_data,testlist):
    authorization_token = signJWT('testuser')  # Implement a function to generate a valid token
    response = client.post("/set_model", json=testlist, headers={"Authorization": 'Bearer '+authorization_token})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

@pytest.mark.parametrize("testlist", [
    # Validate Testing
    {"query": "Test", "use_default": 1,'config':{
        "max_new_tokens": Param.LLM_MAX_NEW_TOKENS,
        "temperature": Param.LLM_TEMPERATURE,
        "top_k": Param.TOP_K,
        "top_p": Param.TOP_P,
        "batch_size": Param.BATCH_SIZE

    },'chat_history':[]},

    {"query": "Test", "use_default": 0, 'config': {
        "max_new_tokens": Param.LLM_MAX_NEW_TOKENS,
        "temperature": Param.LLM_TEMPERATURE-0.1,
        "top_k": Param.TOP_K,
        "top_p": Param.TOP_P,
        "batch_size": Param.BATCH_SIZE+16

    }, 'chat_history': []},
    {"query": "Test", "use_default": 0, 'config': {
        "max_new_tokens": Param.LLM_MAX_NEW_TOKENS,
        "temperature": Param.LLM_TEMPERATURE - 0.2,
        "top_k": Param.TOP_K,
        "top_p": Param.TOP_P,
        "batch_size": Param.BATCH_SIZE + 32

    }, 'chat_history': []},

    {"query": "Test", "use_default": 0, 'config': {
        "max_new_tokens": Param.LLM_MAX_NEW_TOKENS,
        "temperature": Param.LLM_TEMPERATURE - 0.3,
        "top_k": Param.TOP_K,
        "top_p": Param.TOP_P,
        "batch_size": Param.BATCH_SIZE + 32

    }, 'chat_history': []},

])
def test_predict(test_data,testlist):
    authorization_token = signJWT('testuser') # Implement a function to generate a valid token
    response = client.post("/predict", json=testlist, headers={"Authorization": 'Bearer '+authorization_token})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_feedback(test_data):
    authorization_token = signJWT('testuser')  # Implement a function to generate a valid token
    response = client.post("/feedback", json=test_data, headers={"Authorization": 'Bearer '+authorization_token})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

# Implement more test cases as needed to achieve code coverage
