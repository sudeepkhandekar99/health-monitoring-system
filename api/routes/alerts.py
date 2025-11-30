from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.aws_client import get_alerts_table, get_sns_client
from core.config import settings
from models.schemas import Alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


class ManualAlertRequest(BaseModel):
    message: str
    level: str | None = "warning"  # info / warning / critical


@router.post("/patients/{patient_id}/send", response_model=Alert)
async def send_manual_alert(patient_id: str, body: ManualAlertRequest) -> Alert:
    """
    Manually trigger an alert for a patient.
    - Writes to alerts table
    - Publishes to SNS topic
    """
    if not body.message:
        raise HTTPException(status_code=400, detail="Message is required")

    alerts_table = get_alerts_table()
    sns = get_sns_client()

    alert_id = str(uuid.uuid4())
    ts = datetime.now(timezone.utc).isoformat()
    level = body.level or "warning"

    item = {
        "alert_id": alert_id,
        "patient_id": patient_id,
        "created_at": ts,
        "message": body.message,
        "level": level,
        "source": "manual",
    }

    # 1) write to DynamoDB
    alerts_table.put_item(Item=item)

    # 2) publish to SNS (if configured)
    topic_arn = settings.sns_alerts_topic_arn
    if topic_arn:
        sns.publish(
            TopicArn=topic_arn,
            Subject=f"[Manual Alert] Patient {patient_id} - {level.upper()}",
            Message=body.message,
        )

    return Alert(
        alert_id=alert_id,
        patient_id=patient_id,
        created_at=datetime.fromisoformat(ts),
        message=body.message,
        level=level,
        source="manual",
    )