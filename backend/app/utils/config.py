"""
config.py — Centralized settings using Pydantic.

What this does:
  Reads every variable from your .env file and validates them.
  If a required variable is missing, the app crashes at startup
  with a clear error — better than crashing randomly later.

How to use anywhere in the project:
  from app.utils.config import settings
  print(settings.AZURE_OPENAI_ENDPOINT)
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # --- App ---
    APP_ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    SECRET_KEY: str = "change-me-in-production"

    # --- Azure OpenAI ---
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_ENDPOINT: str
    AZURE_OPENAI_DEPLOYMENT_NAME: str = "gpt-4o-email-agent"
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"

    # --- Gmail ---
    GMAIL_CLIENT_ID: str = ""
    GMAIL_CLIENT_SECRET: str = ""
    GMAIL_REDIRECT_URI: str = "http://localhost:8000/auth/gmail/callback"
    GMAIL_TOKEN_FILE: str = "./gmail_token.json"

    # --- Outlook ---
    OUTLOOK_CLIENT_ID: str = ""
    OUTLOOK_CLIENT_SECRET: str = ""
    OUTLOOK_TENANT_ID: str = "common"
    OUTLOOK_REDIRECT_URI: str = "http://localhost:8000/auth/outlook/callback"

    # --- Database ---
    DATABASE_URL: str
    MYSQL_HOST: str = "db"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "email_agent"
    MYSQL_USER: str = "agent_user"
    MYSQL_PASSWORD: str = ""
    MYSQL_ROOT_PASSWORD: str = ""

    # --- Scheduler ---
    POLL_INTERVAL_MINUTES: int = 3

    # --- Azure Resources ---
    AZURE_SUBSCRIPTION_ID: str = ""
    AZURE_RESOURCE_GROUP: str = "email-reply-agent-rg"
    AZURE_LOCATION: str = "eastus"
    ACR_NAME: str = "emailagentacr"
    ACR_LOGIN_SERVER: str = "emailagentacr.azurecr.io"
    AZURE_CONTAINER_APP_NAME: str = "email-reply-agent"
    AZURE_KEY_VAULT_NAME: str = "email-agent-kv"

    # --- Your Profile ---
    YOUR_NAME: str = "Your Name"
    YOUR_VISA_STATUS: str = "OPT STEM"
    YOUR_SKILLS: str = "Machine Learning, Python"
    YOUR_EXPERIENCE_YEARS: int = 2
    YOUR_TARGET_ROLES: str = "ML Engineer, AI Engineer"
    YOUR_LINKEDIN: str = ""
    YOUR_GITHUB: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Returns cached settings.
    lru_cache means .env is only read ONCE at startup — not on every request.
    """
    return Settings()


# Single instance used across the whole app
settings = get_settings()