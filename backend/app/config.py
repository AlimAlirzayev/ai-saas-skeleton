from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    groq_api_key: str
    groq_model: str = "llama-3.1-8b-instant"
    redis_host: str = "redis"
    redis_port: int = 6379

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()