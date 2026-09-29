"""
Application configuration via environment variables.
"""

import os


class Settings:
    APP_VERSION: str = "1.0.0"

    # STT
    STT_SERVICE_URL: str = os.getenv("STT_SERVICE_URL", "http://localhost:8001")

    # Vector DB
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8100"))

    # Odoo
    ODOO_URL: str = os.getenv("ODOO_URL", "http://localhost:8069")
    ODOO_DB: str = os.getenv("ODOO_DB", "odoo_cashier")
    ODOO_USER: str = os.getenv("ODOO_USER", "admin")
    ODOO_PASSWORD: str = os.getenv("ODOO_PASSWORD", "admin")

    # LLM
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.0-flash")

    # Embedding
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-base")

    # Payment
    PAYMENT_API_KEY: str = os.getenv("PAYMENT_API_KEY", "")

    # Email / SMTP
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    # Kitchen Printer
    PRINTER_IP: str = os.getenv("PRINTER_IP", "192.168.1.100")
    PRINTER_PORT: int = int(os.getenv("PRINTER_PORT", "9100"))


settings = Settings()
