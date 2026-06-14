from pydantic import BaseModel
from functools import lru_cache
import os


class Settings(BaseModel):
    # App
    APP_NAME: str = "AI外贸工作平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database - SQLite for local dev, PostgreSQL for production
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_trade.db"
    DATABASE_URL_SYNC: str = "sqlite:///./ai_trade.db"

    # JWT
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # SiliconFlow
    SILICONFLOW_API_KEY: str = ""
    SILICONFLOW_BASE_URL: str = "https://api.siliconflow.cn/v1"

    # AI Models
    AI_MODEL_DAILY: str = "Qwen/Qwen2.5-7B-Instruct"
    AI_MODEL_COMPLEX: str = "deepseek-ai/DeepSeek-V2.5"
    AI_MODEL_VISION: str = "Qwen/Qwen3-VL-8B-Instruct"
    AI_MODEL_EMBED_ZH: str = "BAAI/bge-large-zh-v1.5"
    AI_MODEL_EMBED_EN: str = "BAAI/bge-large-en-v1.5"
    AI_MODEL_IMAGE: str = "stabilityai/stable-diffusion-3.5-large"

    # Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 52428800

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"


@lru_cache()
def get_settings() -> Settings:
    # 从环境变量读取配置
    return Settings(
        APP_NAME=os.getenv("APP_NAME", "AI外贸工作平台"),
        DATABASE_URL=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./ai_trade.db"),
        SECRET_KEY=os.getenv("JWT_SECRET", "change-this-secret-key-in-production"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")),
        SILICONFLOW_API_KEY=os.getenv("SILICONFLOW_API_KEY", ""),
        AI_MODEL_VISION=os.getenv("AI_MODEL_VISION", "Qwen/Qwen3-VL-8B-Instruct"),
    )
