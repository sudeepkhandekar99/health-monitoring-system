from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Query

from app.models.schemas import Patient, VitalReading, Alert

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("/", response_model=List[Patient])
async def list_patients() -> List[Patient]:
    """
    Return a summary list of all patients.
    TODO: Fetch from DynamoDB 'patients' table.
    """
    # placeholder fake data for now
    return [
        Patient(
            patient_id="p1",
            name="John Doe",
            age=65,
            risk_level="warning",
            last_heart_rate=110,
            last_spo2=93,
            last_bp_sys=140,
            last_bp_dia=90,
            last_vital_timestamp=datetime.utcnow(),
        )
    ]


@router.get("/{patient_id}/vitals", response_model=List[VitalReading])
async def get_patient_vitals(
    patient_id: str,
    window_minutes: int = Query(60, ge=5, le=24 * 60),
) -> List[VitalReading]:
    """
    Return vitals for a patient for the given time window (in minutes).
    TODO: Query 'patient_vitals' table filtered by patient_id + timestamp.
    """
    now = datetime.utcnow()
    return [
        VitalReading(
            patient_id=patient_id,
            timestamp=now - timedelta(minutes=5),
            heart_rate=90,
            spo2=96,
            bp_sys=120,
            bp_dia=80,
            is_anomaly=False,
        ),
        VitalReading(
            patient_id=patient_id,
            timestamp=now,
            heart_rate=130,
            spo2=89,
            bp_sys=170,
            bp_dia=100,
            is_anomaly=True,
        ),
    ]


@router.get("/{patient_id}/alerts", response_model=List[Alert])
async def get_patient_alerts(
    patient_id: str,
    limit: int = Query(20, ge=1, le=100),
) -> List[Alert]:
    """
    Return recent alerts for a patient.
    TODO: Query 'alerts' table with GSI on patient_id.
    """
    return [
        Alert(
            alert_id="a1",
            patient_id=patient_id,
            created_at=datetime.utcnow(),
            message="Auto: High heart rate detected",
            level="critical",
            source="auto",
        )
    ][:limit]