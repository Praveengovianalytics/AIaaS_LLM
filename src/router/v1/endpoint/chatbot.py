import os

from fastapi import APIRouter
from ctransformers import AutoModelForCausalLM,AutoTokenizer
import json
import shutil

from langchain.chains import ConversationalRetrievalChain

from core.controller.orchestration_layer.model import LLM
from core.schema.api_response import APIResponse
from core.schema.feedback_request import FeedbackRequest
from core.schema.prediction_request import PredictionRequest
from core.settings import Param
from core.controller.orchestration_layer.embedding_pipeline import EmbeddingPipeline, load_embedding
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import CTransformers

llm = CTransformers(
    model=Param.LLM_MODEL_PATH,
    model_type=Param.LLM_MODEL_TYPE,
    max_new_tokens=Param.LLM_MAX_NEW_TOKENS,
    temperature=Param.LLM_TEMPERATURE
)
router = APIRouter()
from fastapi import FastAPI, File, UploadFile
@router.get("/ping")
def health_check():
    return {"status":'healthy'}

@router.post("/create_embedding")
def create_embedding(file: UploadFile):

    user_folder=Param.EMBEDDING_MODEL_PATH+"zhuofan.chen/"
    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)
    else:
        os.makedirs(user_folder)
    file_location = f"{Param.TEMP_SAVE_PATH}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    embedding=EmbeddingPipeline(file_location,'zhuofan.chen')
    embedding.save_db_local()
    if os.path.isfile(file_location):
        os.remove(file_location)
    return APIResponse(status='success',message='Embedding Created Success')


@router.post("/predict")
def predict(data: PredictionRequest):
    retriever=load_embedding(Param.EMBEDDING_SAVE_PATH+'zhuofan.chen'+"/")
    chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever.as_retriever())
    result=LLM(chain, llm, retriever).predict(data.query,data.chat_history)

    return APIResponse(status='success',message=result)


@router.post("/feedback")
def feedback(data: FeedbackRequest):
    with open(Param.FEEDBACK_LOG_FILE, 'a') as log_file:
        log_file.write(f"User_Timestamp: {data.user_timestamp} | User_Input: {data.chat_history[len(data.chat_history)-2]}\n")
        log_file.write(f"Bot_Timestamp: {data.bot_timestamp} | Bot_Response: {data.chat_history[-1]}\n")
        log_file.write(f"Feedback_Timestamp: {data.feedback_timestamp} | User_Feedback: {data.feedback}\n")
        log_file.write("=" * 50 + "\n")

    return APIResponse(status='success',message='Feedback Noted')




@router.get("/generate_response")
def generate_response(prompt_input: str, temperature: float, top_p: float, user_assistant: str):
    print("user_assistant-",user_assistant)
    user_assistant1 = user_assistant.replace("'", '"')
    user_assistant_data = json.loads(user_assistant1)
    model_path_name = "/Users/praveen/Desktop/LLMs/AIaaS_LLM/BTO_LLM_App/models/llama-2-7b-chat.ggmlv3.q4_0.bin"
    chat_model = AutoModelForCausalLM.from_pretrained(
        model_path_or_repo_id=model_path_name,
        model_type='llama',
        temperature=temperature,
        top_p=top_p,
        hf=True
    )
    tokenizer = AutoTokenizer.from_pretrained(chat_model)
    response = generate_llama2_response(chat_model, prompt_input, user_assistant_data,tokenizer)
    return response

def generate_llama2_response(chat_model, prompt_input, user_assistant,tokenizer):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    response = []

    print(user_assistant)

    for dict_message in user_assistant:
        role = dict_message.get("role")
        content = dict_message.get("content")

        if role == "user" and content:
            string_dialogue += "User: " + content + "\n\n"
        elif content:
            string_dialogue += "Assistant: " + content + "\n\n"

    # You can adjust the parameters as needed
    input_ids = tokenizer.encode(string_dialogue, return_tensors="pt")
    generated_response = chat_model.generate(input_ids,  num_return_sequences=1)

    for item in generated_response:
        decoded_response = tokenizer.decode(item, skip_special_tokens=True)
        response.append(decoded_response)

    return response