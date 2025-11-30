from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Remote Patient Monitoring API"
    aws_region: str = "us-east-1"

    # DynamoDB table names (can override with env vars later)
    patients_table: str = "patients"
    vitals_table: str = "patient_vitals"
    alerts_table: str = "alerts"
    config_table: str = "system_config"

    class Config:
        env_file = ".env"


settings = Settings()