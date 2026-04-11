from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/posdb"

    # Google Sheets（可選）
    GOOGLE_SHEET_ID: str = ""
    GOOGLE_SERVICE_ACCOUNT_JSON: str = ""

    @property
    def sheets_enabled(self) -> bool:
        return bool(self.GOOGLE_SHEET_ID and self.GOOGLE_SERVICE_ACCOUNT_JSON and self.GOOGLE_SERVICE_ACCOUNT_JSON != "{}")

    # Email（可選，不填就不寄信）
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_RECIPIENTS: str = ""

    @property
    def email_enabled(self) -> bool:
        return bool(self.SMTP_USER and self.SMTP_PASSWORD and self.EMAIL_RECIPIENTS)

    # Filtering
    MIN_ORDER_AMOUNT: int = 1000

    # Webhook
    WEBHOOK_SECRET: str = ""  # optional: POS signs payload with this secret

    class Config:
        env_file = ".env"

    def get_recipients(self) -> List[str]:
        return [e.strip() for e in self.EMAIL_RECIPIENTS.split(",") if e.strip()]


settings = Settings()
