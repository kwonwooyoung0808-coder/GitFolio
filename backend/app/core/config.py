from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    CLAUDE_MODEL: str = "claude-sonnet-4-6"
    OPENAI_FALLBACK_MODEL: str = "gpt-4o-mini"
    USE_CLOUD_LLM: bool = False
    OLLAMA_ENABLED: bool = True
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    OLLAMA_TIMEOUT_SECONDS: int = 90
    ENABLE_PDF: bool = True

    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str = "http://127.0.0.1:8000/api/v1/auth/github/callback"

    DATABASE_URL: str = "sqlite:///./gitfolio.db"

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    FRONTEND_URL: str = "http://localhost:5173"
    ENV: str = "development"
    REPORTS_DIR: str = "generated_reports"

    class Config:
        env_file = ".env"


settings = Settings()
