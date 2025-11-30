from fastapi import APIRouter

from app.models.schemas import StreamStatus

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stream/status", response_model=StreamStatus)
async def get_stream_status() -> StreamStatus:
    """
    Get current synthetic streaming status (ON/OFF).
    TODO: Read from 'system_config' DynamoDB table.
    """
    # placeholder
    return StreamStatus(status="ON")


@router.post("/stream/start", response_model=StreamStatus)
async def start_stream() -> StreamStatus:
    """
    Turn ON synthetic data streaming.
    TODO: Update 'system_config' table.
    """
    return StreamStatus(status="ON")


@router.post("/stream/stop", response_model=StreamStatus)
async def stop_stream() -> StreamStatus:
    """
    Turn OFF synthetic data streaming.
    TODO: Update 'system_config' table.
    """
    return StreamStatus(status="OFF")