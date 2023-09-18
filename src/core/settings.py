class Param:
    APP_PATH='/Users/P1359690/backend_ai/'
    DB_FAISS_PATH = f"{APP_PATH}embeddings/db_faiss"
    CHAT_LOG_PATH = 'logs/feedback_log.txt'
    LLM_MODEL_PATH = f"{APP_PATH}models/llama-2-7b-chat.ggmlv3.q4_K_S.bin"
    LLM_MODEL_TYPE = "llama"
    LLM_MAX_NEW_TOKENS = 512
    LLM_TEMPERATURE = 0.5
    EMBEDDING_MODEL_PATH = f"{APP_PATH}models/all-MiniLM-L6-v2"
    EMBEDDING_MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
    EMBEDDING_DEVICE = 'cpu'
    CSV_DELIMITER = ','
    CSV_ENCODING = "utf-8"
    TEMP_SAVE_PATH = f"{APP_PATH}/src/static/temp/"
    EMBEDDING_SAVE_PATH=f"{APP_PATH}/src/static/embedding/"

    FEEDBACK_LOG_FILE = f"{APP_PATH}logs/feedback_log.txt"
    AUTH_HASH_PASS_FILE = f"{APP_PATH}/src/core/secret/hashed_passwords.txt"