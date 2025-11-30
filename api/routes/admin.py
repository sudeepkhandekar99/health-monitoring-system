from fastapi import APIRouter

from core.aws_client import get_config_table
from models.schemas import StreamStatus

router = APIRouter(prefix="/admin", tags=["admin"])


def _get_stream_status_value() -> str:
    table = get_config_table()
    resp = table.get_item(Key={"key": "stream_status"})
    item = resp.get("Item")
    if not item:
        return "OFF"
    return item.get("value", "OFF")


@router.get("/stream/status", response_model=StreamStatus)
async def get_stream_status() -> StreamStatus:
    """
    Get current synthetic streaming status (ON/OFF).
    Reads from system_config table.
    """
    status = _get_stream_status_value()
    return StreamStatus(status=status)


@router.post("/stream/start", response_model=StreamStatus)
async def start_stream() -> StreamStatus:
    """
    Turn ON synthetic data streaming.
    Updates system_config.stream_status = ON
    """
    table = get_config_table()
    table.put_item(Item={"key": "stream_status", "value": "ON"})
    return StreamStatus(status="ON")


@router.post("/stream/stop", response_model=StreamStatus)
async def stop_stream() -> StreamStatus:
    """
    Turn OFF synthetic data streaming.
    Updates system_config.stream_status = OFF
    """
    table = get_config_table()
    table.put_item(Item={"key": "stream_status", "value": "OFF"})
    return StreamStatus(status="OFF")