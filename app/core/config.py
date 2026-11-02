import os
import secrets

class Settings:
    APP_NAME = os.getenv("APP_NAME", "AnimalCare AI API")
    API_V1_PREFIX = "/api/v1"
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:4200,http://127.0.0.1:4200"
    ).split(",")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or secrets.token_urlsafe(32)
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    AUTH_REQUIRED = os.getenv("AUTH_REQUIRED", "false").lower() == "true"

settings = Settings()
