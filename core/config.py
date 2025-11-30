# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",      # load from .env
        env_file_encoding="utf-8",
        extra="ignore",       # ignore any extra env vars
        env_prefix="",        # use exact names (APP_NAME, AWS_REGION, etc.)
    )

    # App metadata
    app_name: str = "Remote Patient Monitoring API"
    environment: str = "development"

    # AWS
    aws_region: str = "us-east-1"

    # DynamoDB tables
    patients_table: str = "patients"
    vitals_table: str = "patient_vitals"
    alerts_table: str = "alerts"
    config_table: str = "system_config"

    # SNS
    sns_alerts_topic_arn: str = ""

    # Server options (used later if you want)
    host: str = "0.0.0.0"
    port: int = 8000

    # Admin
    admin_api_key: str = "dev-admin-key"


settings = Settings()