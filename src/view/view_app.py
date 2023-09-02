import os
from ctransformers import AutoModelForCausalLM
import requests

def show_chat_app(st, session_state_username):
    st.write("Welcome ", session_state_username)

    

    # Replicate Credentials
    with st.sidebar:
        st.title("BTO Chatbot")

        # Refactored from <https://github.com/a16z-infra/llama2-chatbot>
        st.subheader("Models and parameters")
        temperature = st.sidebar.slider(
            "temperature", min_value=0.01, max_value=2.0, value=0.1, step=0.01
        )
        top_p = st.sidebar.slider(
            "top_p", min_value=0.01, max_value=1.0, value=0.9, step=0.01
        )
        # max_length = st.sidebar.slider('max_length', min_value=64, max_value=4096, value=512, step=8)
        # st.markdown('📖 Learn how to build this app in this [blog](#link-to-blog)!')

    # Store LLM generated responses
    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": "How may I assist you today?"}
        ]

    # Display or clear chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    def clear_chat_history():
        st.session_state.messages = [
            {"role": "assistant", "content": "How may I assist you today?"}
        ]

    st.sidebar.button("Clear Chat History", on_click=clear_chat_history)

    # Function for generating LLaMA2 response using FastAPI endpoint
    @st.cache_resource()
    def generate_llama2_response(prompt_input,temperature,top_p,user_assistant):

        url = "http://localhost:8000/generate_response"
        data = {
            "prompt_input": prompt_input,
            "temperature": temperature,
            "top_p": top_p,
            "user_assistant": str(user_assistant)
        }
        response = requests.get(url,params=data)
        return response.text  # You might need to parse the response as needed


    # User-provided prompt
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Generate a new response if last message is not from assistant
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                user_assistant = st.session_state.messages
                st.write("user_assistant",user_assistant)
                response = generate_llama2_response(prompt,temperature,top_p,user_assistant)
                placeholder = st.empty()
                full_response = ""
                for item in response:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
