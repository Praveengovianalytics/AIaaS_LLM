class Param:
    """Configure Settings for Application"""
    USE_GPU= True
    APP_PATH = "/home/praveengovi_nlp/AIaaS_Projects/AIaas_LLM/AIaaS_LLM/"
    PORT_NUMBER=8000
    RUNNING_ADDRESS="0.0.0.0"
    DB_FAISS_PATH = f"{APP_PATH}embeddings/db_faiss"
    CHAT_LOG_PATH = "logs/feedback_log.txt"
    LLM_MODEL_TYPE = "llama"
    # Default Model Configuration
    LLM_MODEL = {
        'mistral-7b': f"{APP_PATH}models/mistral-7b-openorca.Q4_K_M.gguf",
        'zephyr-7b': f"{APP_PATH}models/zephyr-7b-beta.Q4_K_M.gguf",
                      'llama2-7b': f"{APP_PATH}models/llama-2-7b-chat.Q4_K_M.gguf",
        'llama2-13b': f"{APP_PATH}models/llama-2-13b-chat.Q4_K_M.gguf"


    }
    DATA_LLM_MODEL = {
        'WizardCoder-34B': f"{APP_PATH}models/WizardLM-WizardCoder-Python-34B-V1.0.Q4_K_M.gguf",
        'Ziya-34B': f"{APP_PATH}models/ziya-coding-34b-v1.0.Q4_K_M.gguf",
        'CodeFuse-34B': f"{APP_PATH}models/codefuse-codellama-34b.Q4_K_M.gguf"

    }
    LLM_MAX_NEW_TOKENS = 4000
    LLM_TEMPERATURE = 0.4
    BATCH_SIZE = 256
    TOP_K = 40
    TOP_P = 0.95
    LLM_CONTEXT_LENGTH = 4000
    # Ethic Control
    POST_CONTROL = False
    JAILBREAK_CONTROL = False
    # Prompt and Fetching Settings
    FETCH_INDEX = 20000
    SELECT_INDEX = 10
    SYSTEM_PROMPT = ("Do note that Your are a data dictionary bot. Your task is to fully answer the user's query based "
                     "on the information provided to you.")
    EMBEDDING_MODEL_PATH = f"{APP_PATH}models/bge-large-en"
    EMBEDDING_MODEL_NAME = "BAAI/bge-large-en"
    EMBEDDING_DEVICE = "cuda"
    CSV_DELIMITER = ","
    CSV_ENCODING = "utf-8"
    TEMP_SAVE_PATH = f"{APP_PATH}/src/static/temp/"
    EMBEDDING_SAVE_PATH = f"{APP_PATH}/src/static/embedding/"
    ENVIRONMENT= 'DEV'
    VERSION_INFO='0.1'
    LOG_PATH=f"{APP_PATH}/src/static/logs/"
    # binascii.hexlify(os.urandom(128))
    JWT_SECRET_KEY = "f0c6cdaecbf5383e6b1a74df438574ad0c16a64c03da143b1c078003a305db077224d5ff1ad08761c293b3f6c2513b294a02da22b88596265718cd53b895fc49c9198587cd811a852f1a118856285f419336b7e49421c413f1a9967ff9445613d6d272ac9459c7b89444a7ec31a72e6f840aaa7f9e4dee96de228866c36596c3"
    JWT_ALGORITHM = "HS256"
    JWT_API_SECRET_KEY="45bebf8e71187ac76126a32edc9a93959050cf2ce039a887ae76c63e39774e5ca03605d5680e52ca02b946f418262207c0eb323744416afda966afc69e0e621b5e2ec750f1041b44d5b0aa295390ef151d387579c02b55dc99bd80115979524b3e311efd6fbc61dd9186d06bd6fae0588d6935707bbf186bdd26ae67bf25592f"
    JWT_API_ALGORITHM = "HS256"
    FEEDBACK_LOG_FILE = f"{APP_PATH}/src/static/logs/"
    AUTH_HASH_PASS_FILE = f"{APP_PATH}/src/core/secret/hashed_passwords.txt"
    CUSTOMER_INFO = f"{APP_PATH}/src/core/secret/customer_data.txt"

