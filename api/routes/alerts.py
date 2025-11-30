from datetime import datetime

from fastapi import APIRouter, HTTPException
from models.schemas import Alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/patients/{patient_id}/send", response_model=Alert)
async def send_manual_alert(patient_id: str, message: str) -> Alert:
    """
    Manually trigger an alert for a patient.
    TODO: Persist alert to DynamoDB and publish to SNS.
    """
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")

    alert = Alert(
        alert_id="manual-temp-id",  # later: use uuid
        patient_id=patient_id,
        created_at=datetime.utcnow(),
        message=message,
        level="warning",
        source="manual",
    )
    # TODO: write to alerts table + SNS publish
    return alert