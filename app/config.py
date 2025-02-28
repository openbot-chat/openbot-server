import os
import logging
from dotenv import load_dotenv

load_dotenv(verbose=True)


ENV = os.getenv("ENV", "development")
PROXY = os.getenv("PROXY")
if PROXY is not None:
    import openai

    openai.proxy = PROXY
    logging.info(f"set proxy for openai: {PROXY}")


AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN")
AUTH0_AUDIENCE: str = os.getenv("AUTH0_AUDIENCE")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://root:openbot@localhost:5432/llm")
DEBUG_DATABASE_ECHO: str = os.getenv("DEBUG_DATABASE_ECHO", "")
DATABASE_POOL_SIZE: int = os.getenv("DATABASE_POOL_SIZE", 10)
DATABASE_MAX_OVERFLOW: int = os.getenv("DATABASE_MAX_OVERFLOW", 10)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORGANIZATION = os.getenv("OPENAI_ORGANIZATION")


CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

DEFAULT_QDRANT_OPTIONS = {
    "url": os.getenv("QDRANT_URL"),
    "api_key": os.getenv("QDRANT_API_KEY"),
}

GATEWAY_API_KEY = os.getenv("GATEWAY_API_KEY")

ZEP_API_URL = os.getenv("ZEP_API_URL")
ZEP_API_KEY = os.getenv("ZEP_API_KEY")

PAYMENT_API_KEY = os.getenv("PAYMENT_API_KEY")
PAYMENT_API_SECRET = os.getenv("PAYMENT_API_SECRET")
PAYMENT_WEBHOOK_SECRET = os.getenv("PAYMENT_WEBHOOK_SECRET")
PAYMENT_BASE_URL = os.getenv("PAYMENT_BASE_URL")
PAYMENT_PLAN = os.getenv("PAYMENT_PLAN")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
