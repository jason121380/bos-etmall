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

    # Email via Zeabur Email（可選，不填就不寄信）
    ZEABUR_EMAIL_API_KEY: str = ""
    EMAIL_FROM: str = ""        # 發件人，需為已綁定網域，例如 report@yourdomain.com
    EMAIL_RECIPIENTS: str = ""  # 收件人，逗號分隔

    @property
    def email_enabled(self) -> bool:
        # 只要有 API Key 和發件人就啟用排程（收件人可從後台 DB 設定）
        return bool(self.ZEABUR_EMAIL_API_KEY and self.EMAIL_FROM)

    # Filtering
    MIN_ORDER_AMOUNT: int = 1000

    # Webhook
    WEBHOOK_SECRET: str = ""  # optional: POS signs payload with this secret

    class Config:
        env_file = ".env"

    def get_recipients(self) -> List[str]:
        return [e.strip() for e in self.EMAIL_RECIPIENTS.split(",") if e.strip()]


settings = Settings()
