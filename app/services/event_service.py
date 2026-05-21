from sqlalchemy.orm import Session

from app.models.event_log import EventLog
from app.schemas.device_data import DeviceDataSchema


# Evaluate device event and store evaluation log
def evaluate_device_event( db: Session, payload: DeviceDataSchema, current_zone: str, event_type: str):

    evaluation_result = None

    if current_zone is not None:
        # Critical: Restricted zone + high heart rate
        if (
            payload.heart_rate > 120 and current_zone == "Restricted Zone" ):
            evaluation_result = {
                "event": "High Heart Rate in Restricted Zone",
                "severity": "High",
                "status": "Flagged",
                "reason": "Heart rate exceeded threshold inside restricted zone"
            }

        # High activity in research lab
        elif ( payload.steps > 10000 and current_zone == "Research Lab Zone"):
            evaluation_result = {
                "event": "Unusual Activity in Research Lab",
                "severity": "Medium",
                "status": "Monitor",
                "reason": "High movement detected inside research lab"
            }

        # Entry into restricted zone
        elif ( event_type == "ENTRY" and current_zone == "Restricted Zone"):
            evaluation_result = {
                "event": "Restricted Zone Entry",
                "severity": "Medium",
                "status": "Flagged",
                "reason": "Device entered restricted zone"
            }

        # Low activity in warehouse
        elif (payload.steps < 50 and current_zone == "Warehouse Zone" ):
            evaluation_result = {
                "event": "Low Activity in Warehouse",
                "severity": "Low",
                "status": "Monitor",
                "reason": "Very low movement detected in warehouse zone"
            }

        # Elevated heart rate in office
        elif (payload.heart_rate > 100 and current_zone == "Office Zone"):
            evaluation_result = {
                "event": "Elevated Heart Rate in Office",
                "severity": "Low",
                "status": "Warning",
                "reason": "Heart rate above normal office threshold"
            }

        # Parking zone entry
        elif (event_type == "ENTRY" and current_zone == "Parking Zone"):
            evaluation_result = {
                "event": "Parking Zone Entry",
                "severity": "Low",
                "status": "Info",
                "reason": "Device entered parking zone"
            }
    # CASE 2: OUTSIDE ALL ZONES
    else:
        # High heart rate outside geofence
        if payload.heart_rate > 120:
            evaluation_result = {
                "event": "High Heart Rate Outside Zone",
                "severity": "Medium",
                "status": "Warning",
                "reason": "Heart rate > 120 but device is outside all geofences"
            }

        # Very low activity outside geofence
        elif payload.steps < 50:
            evaluation_result = {
                "event": "Inactive Device Outside Zone",
                "severity": "Low",
                "status": "Monitor",
                "reason": "Low movement detected outside geofences"
            }

    # STORE EVENT IN DB
    if evaluation_result:

        event_log = EventLog(
            device_id=payload.device_id,
            event_type=evaluation_result["event"],
            severity=evaluation_result["severity"],
            status=evaluation_result["status"],
            zone=current_zone,
            reason=evaluation_result["reason"],
            heart_rate=payload.heart_rate,
            latitude=payload.location.lat,
            longitude=payload.location.lng
        )

        db.add(event_log)
        db.commit()
        db.refresh(event_log)

    return evaluation_result