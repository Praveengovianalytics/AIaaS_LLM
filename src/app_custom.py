import streamlit as st 
from streamlit_chat import message
import tempfile
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import CTransformers
from langchain.chains import ConversationalRetrievalChain
import os
import datetime

DB_FAISS_PATH = 'embedding_layer/db_faiss'
CHAT_LOG_PATH = 'logs/feedback_log.txt'

def save_feedback_to_log(user_timestamp, user_input, bot_timestamp, bot_response, feedback_timestamp, feedback):
    """Function to save feedback to a log file."""
    with open('feedback_log.txt', 'a') as log_file:
        log_file.write(f"User_Timestamp: {user_timestamp} | User_Input: {user_input}\n")
        log_file.write(f"Bot_Timestamp: {bot_timestamp} | Bot_Response: {bot_response}\n")
        log_file.write(f"Feedback_Timestamp: {feedback_timestamp} | User_Feedback: {feedback}\n")
        log_file.write("="*50 + "\n")

#Loading the model
def load_llm():
    # Load the locally downloaded model here
    model_path_or_repo_id='/Users/praveen/Desktop/LLMs/AIaaS_LLM/AI-DataSteward/ai-datasteward/models/codellama-7b-instruct.Q4_K_S.gguf'
    llm = CTransformers(
        model = model_path_or_repo_id,
        model_type="llama",
        max_new_tokens = 512,
        temperature = 0.5
    )
    return llm

st.title("BTO GenAI - Appstore - AI-Datasteward")

uploaded_file = st.sidebar.file_uploader("Upload your Data", type="csv")

if uploaded_file :
   #use tempfile because CSVLoader only accepts a file_path
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    loader = CSVLoader(file_path=tmp_file_path, encoding="utf-8", csv_args={
                'delimiter': ','})
    data = loader.load()
    #st.json(data)
    embedding_model_path='/Users/praveen/Desktop/LLMs/AIaaS_LLM/AI-DataSteward/ai-datasteward/models/all-MiniLM-L6-v2_model'
    #model_name='sentence-transformers/all-MiniLM-L6-v2'
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_path,
                                       model_kwargs={'device': 'cpu'})

    db = FAISS.from_documents(data, embeddings)
    db.save_local(DB_FAISS_PATH)
    llm = load_llm()
    chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=db.as_retriever())

    def conversational_chat(query):
        result = chain({"question": query, "chat_history": st.session_state['history']})
        st.session_state['history'].append((query, result["answer"]))
        return result["answer"]

    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["Hello ! Ask me anything about " + uploaded_file.name + " 🤗"]

    if 'past' not in st.session_state:
        st.session_state['past'] = ["Hey ! 👋"]

    #container for the chat history
    response_container = st.container()
    #container for the user's text input
    container = st.container()

    with container:

        with st.form(key='my_form', clear_on_submit=True):

            if 'user_timestamp' not in st.session_state:
                st.session_state['user_timestamp'] = ""

            if 'bot_timestamp' not in st.session_state:
                st.session_state['bot_timestamp'] = ""

            user_input = st.text_input("Query:", placeholder="Talk to your csv data here (:", key='input')
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:

            st.session_state['user_timestamp']  = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Capture user's timestamp
            output = conversational_chat(user_input)
            st.session_state['bot_timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Capture bot's timestamp

            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

    if st.session_state['generated']:
        with response_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="big-smile")

                message(st.session_state["generated"][i], key=str(i), avatar_style="thumbs")
        # Only display feedback if there's a latest generated response
        if len(st.session_state['generated']) > 1:
        # Collect feedback
            feedback_options = ["😃 Useful", "😐 Ok", "😞 Not-Useful"]
            feedback = st.radio("Provide feedback on the response:", feedback_options, key='feedback_radio',horizontal=True)
            feedback_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Capture feedback's timestamp
            if st.button("Submit Feedback"):
                save_feedback_to_log(st.session_state['user_timestamp'], st.session_state["past"][-1], st.session_state['bot_timestamp'], st.session_state["generated"][-1], feedback_timestamp, feedback)
                st.success("Thanks for the feedback!")
