import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Voice Synthesis Microservice"
    MODEL_ID: str = "african-low-resource/omnivoice-amharic"
    DEVICE: str = "cuda:0" if os.environ.get("USE_CUDA", "1") == "1" else "cpu"
    DTYPE: str = "float16"
    SAMPLE_RATE: int = 24000
    MAX_CHUNK_CHARS: int = 120
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379")

    class Config:
        env_file = ".env"

settings = Settings()