from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chat Bot API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "A chat bot API using LangChain and LangGraph"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./chatbot.db"
    
    # Authentication Settings
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Admin Settings
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"
    
    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    MODEL_NAME: str = "gpt-3.5-turbo"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Webhook Settings
    WEBHOOK_SECRET: Optional[str] = None
    WEBHOOK_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()