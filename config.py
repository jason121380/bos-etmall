from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/posdb"

    # Google Sheets
    GOOGLE_SHEET_ID: str = ""
    GOOGLE_SERVICE_ACCOUNT_JSON: str = ""  # JSON string of service account credentials

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""  # Gmail App Password
    EMAIL_RECIPIENTS: str = ""  # comma-separated emails

    # Filtering
    MIN_ORDER_AMOUNT: int = 1000

    # Webhook
    WEBHOOK_SECRET: str = ""  # optional: POS signs payload with this secret

    class Config:
        env_file = ".env"

    def get_recipients(self) -> List[str]:
        return [e.strip() for e in self.EMAIL_RECIPIENTS.split(",") if e.strip()]


settings = Settings()
