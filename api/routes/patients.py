from datetime import datetime, timedelta, timezone
from typing import List

from boto3.dynamodb.conditions import Key
from fastapi import APIRouter, Query

from core.aws_client import get_patients_table, get_vitals_table, get_alerts_table
from models.schemas import Patient, VitalReading, Alert

router = APIRouter(prefix="/patients", tags=["patients"])


def _parse_ts(ts: str | None):
    if not ts:
        return None
    try:
        # assume ISO format
        return datetime.fromisoformat(ts)
    except Exception:
        return None


@router.get("/", response_model=List[Patient])
async def list_patients() -> List[Patient]:
    """
    Return a summary list of all patients with last vitals + risk_level.
    Uses a DynamoDB Scan (fine for demo-sized data).
    """
    table = get_patients_table()
    resp = table.scan()
    items = resp.get("Items", [])

    patients: list[Patient] = []
    for item in items:
        patients.append(
            Patient(
                patient_id=item["patient_id"],
                name=item.get("name", ""),
                age=item.get("age"),
                sex=item.get("sex"),
                risk_level=item.get("risk_level", "normal"),
                last_heart_rate=item.get("last_heart_rate"),
                last_spo2=item.get("last_spo2"),
                last_bp_sys=item.get("last_bp_sys"),
                last_bp_dia=item.get("last_bp_dia"),
                last_vital_timestamp=_parse_ts(item.get("last_vital_timestamp")),
            )
        )
    return patients


@router.get("/{patient_id}/vitals", response_model=List[VitalReading])
async def get_patient_vitals(
    patient_id: str,
    window: int = Query(60, ge=5, le=24 * 60, description="Time window in minutes"),
) -> List[VitalReading]:
    """
    Return vitals for a patient for the given time window (in minutes).
    Reads from patient_vitals table using PK + timestamp range.
    """
    table = get_vitals_table()

    now = datetime.now(timezone.utc)
    start_time = now - timedelta(minutes=window)

    start_iso = start_time.isoformat()
    end_iso = now.isoformat()

    resp = table.query(
        KeyConditionExpression=Key("patient_id").eq(patient_id)
        & Key("timestamp").between(start_iso, end_iso),
    )
    items = resp.get("Items", [])

    readings: list[VitalReading] = []
    for item in items:
        readings.append(
            VitalReading(
                patient_id=item["patient_id"],
                timestamp=_parse_ts(item["timestamp"]),
                heart_rate=int(item["heart_rate"]),
                spo2=int(item["spo2"]),
                bp_sys=int(item["bp_sys"]),
                bp_dia=int(item["bp_dia"]),
                is_anomaly=bool(item.get("is_anomaly", False)),
            )
        )
    # DynamoDB already returns sorted by sort key, but OK as-is.
    return readings


@router.get("/{patient_id}/alerts", response_model=List[Alert])
async def get_patient_alerts(
    patient_id: str,
    limit: int = Query(20, ge=1, le=100),
) -> List[Alert]:
    """
    Return recent alerts for a patient.
    Uses alerts table GSI: patient_id_index.
    """
    table = get_alerts_table()

    resp = table.query(
        IndexName="patient_id_index",
        KeyConditionExpression=Key("patient_id").eq(patient_id),
        Limit=limit,
        ScanIndexForward=False,  # newest first (if sorted on alert_id/timestamp pattern)
    )
    items = resp.get("Items", [])

    alerts: list[Alert] = []
    for item in items:
        alerts.append(
            Alert(
                alert_id=item["alert_id"],
                patient_id=item["patient_id"],
                created_at=_parse_ts(item.get("created_at")),
                message=item.get("message", ""),
                level=item.get("level", "warning"),
                source=item.get("source", "auto"),
            )
        )
    return alerts