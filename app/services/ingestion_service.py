from sqlalchemy.orm import Session

from app.models.device_data import DeviceData
from app.schemas.device_data import DeviceDataSchema
from app.services.geofence_service import detect_zone, detect_zone_event
from app.services.event_service import evaluate_device_event


async def ingest_device_data(payload: DeviceDataSchema, db: Session) -> dict:

    # Detect current zone
    current_zone = detect_zone(payload.location.lat, payload.location.lng)
    # Fetch last device state
    last_status = get_last_device_status(db, payload.device_id)

    previous_zone = last_status.zone if last_status else None

    # Detect entry/exit/stay event
    event_type = detect_zone_event(previous_zone, current_zone)

    # Store raw telemetry with event_type
    device_data = save_device_data(db, payload, current_zone, event_type)

    # Evaluate and store intelligent event log
    evaluate_device_event(db, payload, current_zone, event_type)

    return build_response(device_data, current_zone, event_type, last_status)


def save_device_data(db: Session, payload: DeviceDataSchema, current_zone: str, event_type: str):

    device_data = DeviceData(
        device_id=payload.device_id,
        heart_rate=payload.heart_rate,
        steps=payload.steps,
        latitude=payload.location.lat,
        longitude=payload.location.lng,
        zone=current_zone,
        event_type=event_type
    )

    db.add(device_data)
    db.commit()
    db.refresh(device_data)
    return device_data


# Build API response
def build_response(device_data: DeviceData, current_zone: str, event_type: str, last_status):

    return {
        "status": "success",
        "message": "Device data stored successfully",
        "data": {
            "id": device_data.id,
            "device_id": device_data.device_id,
            "zone": current_zone,
            "event_type": event_type,
            "created_at": device_data.created_at
        },
        "is_first_record": last_status is None
    }


# Fetch latest device state
def get_last_device_status(db: Session, device_id: str):

    return (
        db.query(DeviceData)
        .filter(DeviceData.device_id == device_id)
        .order_by(DeviceData.created_at.desc())
        .first()
    )