class Param:
    """Configure Settings for Application"""

    APP_PATH = "/Users/P1359690/backend_ai/"
    PORT_NUMBER=8000
    RUNNING_ADDRESS="localhost"
    DB_FAISS_PATH = f"{APP_PATH}embeddings/db_faiss"
    CHAT_LOG_PATH = "logs/feedback_log.txt"
    LLM_MODEL_PATH = f"{APP_PATH}models/llama-2-7b-chat.ggmlv3.q4_K_S.bin"
    LLM_MODEL_TYPE = "llama"
    LLM_MAX_NEW_TOKENS = 1200
    LLM_TEMPERATURE = 0.4
    BATCH_SIZE = 256
    TOP_K = 40
    TOP_P=0.95
    EMBEDDING_MODEL_PATH = f"{APP_PATH}models/all-MiniLM-L6-v2"
    EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE = "cpu"
    CSV_DELIMITER = ","
    CSV_ENCODING = "utf-8"
    TEMP_SAVE_PATH = f"{APP_PATH}/src/static/temp/"
    EMBEDDING_SAVE_PATH = f"{APP_PATH}/src/static/embedding/"
    # binascii.hexlify(os.urandom(128))
    JWT_SECRET_KEY = "f0c6cdaecbf5383e6b1a74df438574ad0c16a64c03da143b1c078003a305db077224d5ff1ad08761c293b3f6c2513b294a02da22b88596265718cd53b895fc49c9198587cd811a852f1a118856285f419336b7e49421c413f1a9967ff9445613d6d272ac9459c7b89444a7ec31a72e6f840aaa7f9e4dee96de228866c36596c3"
    JWT_ALGORITHM = "HS256"
    FEEDBACK_LOG_FILE = f"{APP_PATH}/src/static/logs/"
    AUTH_HASH_PASS_FILE = f"{APP_PATH}/src/core/secret/hashed_passwords.txt"
