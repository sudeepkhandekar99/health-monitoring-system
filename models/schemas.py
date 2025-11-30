from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Patient(BaseModel):
    patient_id: str = Field(..., description="Unique ID of the patient")
    name: str
    age: Optional[int] = None
    sex: Optional[Literal["M", "F", "O"]] = None

    risk_level: Literal["normal", "warning", "critical"] = "normal"
    last_vital_timestamp: Optional[datetime] = None
    last_heart_rate: Optional[int] = None
    last_spo2: Optional[int] = None
    last_bp_sys: Optional[int] = None
    last_bp_dia: Optional[int] = None


class VitalReading(BaseModel):
    patient_id: str
    timestamp: datetime
    heart_rate: int
    spo2: int
    bp_sys: int
    bp_dia: int
    is_anomaly: bool = False


class Alert(BaseModel):
    alert_id: Optional[str] = None
    patient_id: str
    created_at: Optional[datetime] = None
    message: str
    level: Literal["info", "warning", "critical"] = "warning"
    source: Literal["auto", "manual"] = "auto"


class StreamStatus(BaseModel):
    status: Literal["ON", "OFF"]