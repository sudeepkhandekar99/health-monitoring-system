from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Load .env automatically
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "Health Monitoring System"
    environment: str = "development"

    # AWS
    aws_region: str

    # DynamoDB tables
    patients_table: str
    vitals_table: str
    alerts_table: str
    config_table: str

    # SNS
    sns_alerts_topic_arn: str | None = None

    # Server config
    host: str = "0.0.0.0"
    port: int = 8000


# Create global settings instance
settings = Settings()