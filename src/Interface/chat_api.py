from fastapi import FastAPI
from ctransformers import AutoModelForCausalLM,AutoTokenizer
import uvicorn
import json

app = FastAPI()


@app.get("/generate_response")
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



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

