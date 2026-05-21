from sqlalchemy.orm import Session

from app.models.event_log import EventLog
from app.schemas.device_data import DeviceDataSchema

# Get all events
def get_all_events(db: Session):
    events = (
        db.query(EventLog)
        .order_by(EventLog.created_at.desc())
        .all()
    )

    return {
        "status": "success",
        "count": len(events),
        "data": events
    }

# Get only high severity alerts
def get_alerts(db: Session):

    alerts = (
        db.query(EventLog)
        .filter(EventLog.severity == "High")
        .order_by(EventLog.created_at.desc())
        .all()
    )

    return {
        "status": "success",
        "count": len(alerts),
        "data": alerts
    }

# Get events for specific device
def get_device_events(db: Session, device_id: str):

    events = (
        db.query(EventLog)
        .filter(EventLog.device_id == device_id)
        .order_by(EventLog.created_at.desc())
        .all()
    )

    return {
        "status": "success",
        "device_id": device_id,
        "count": len(events),
        "data": events
    }


# Summary report (RFP-style analytics)
def get_summary_report(db: Session):

    events = db.query(EventLog).all()

    total_events = len(events)
    high_severity_events = len([e for e in events if e.severity == "High"])

    zone_activity = {}

    for e in events:
        zone_activity[e.zone] = zone_activity.get(e.zone, 0) + 1

    return {
        "status": "success",
        "total_events": total_events,
        "high_severity_events": high_severity_events,
        "zone_activity": zone_activity
    }

def evaluate_device_event(db: Session, payload: DeviceDataSchema, current_zone: str, event_type: str):

    hr, steps, zone = payload.heart_rate, payload.steps, current_zone

    evaluation_result = {
        "event": f"Normal Activity in {zone}",
        "severity": "Info",
        "status": "OK",
        "reason": "Heart rate within normal range AND activity level normal"
    }

    if zone == "OUTSIDE":

        if hr > 120:
            evaluation_result = {
                "event": "High Heart Rate Outside Zone",
                "severity": "Medium",
                "status": "Warning",
                "reason": "Heart rate > 120 AND outside all geofences"
            }

        elif steps < 50:
            evaluation_result = {
                "event": "Inactive Device Outside Zone",
                "severity": "Low",
                "status": "Monitor",
                "reason": "Steps < 50 AND outside all geofences"
            }

    else:

        if hr > 140:
            evaluation_result = {
                "event": "Emergency Heart Rate Detected",
                "severity": "Critical",
                "status": "Emergency",
                "reason": "Heart rate > 140 AND abnormal physiological condition detected"
            }

        elif hr > 120 and zone == "Restricted Zone":
            evaluation_result = {
                "event": "Critical Health Risk in Restricted Zone",
                "severity": "High",
                "status": "Alert",
                "reason": "Heart rate > 120 AND inside restricted zone"
            }

        elif steps > 10000 and zone == "Research Lab Zone":
            evaluation_result = {
                "event": "Unusual High Activity in Research Lab",
                "severity": "Medium",
                "status": "Monitor",
                "reason": "Steps > 10000 AND inside research lab zone"
            }

        elif event_type == "ENTRY" and zone == "Restricted Zone":
            evaluation_result = {
                "event": "Restricted Zone Entry",
                "severity": "Medium",
                "status": "Flagged",
                "reason": "Event = ENTRY AND zone = Restricted Zone"
            }

        elif hr > 100 and zone == "Office Zone":
            evaluation_result = {
                "event": "Elevated Heart Rate in Office",
                "severity": "Low",
                "status": "Warning",
                "reason": "Heart rate > 100 AND inside office zone"
            }

        elif steps < 50 and zone == "Warehouse Zone":
            evaluation_result = {
                "event": "Low Activity in Warehouse",
                "severity": "Low",
                "status": "Monitor",
                "reason": "Steps < 50 AND inside warehouse zone"
            }

        elif event_type == "ENTRY" and zone == "Parking Zone":
            evaluation_result = {
                "event": "Parking Zone Entry",
                "severity": "Info",
                "status": "OK",
                "reason": "Event = ENTRY AND inside parking zone"
            }

    event_log = EventLog(
        device_id=payload.device_id,
        event=evaluation_result["event"],
        severity=evaluation_result["severity"],
        status=evaluation_result["status"],
        zone=zone,
        reason=evaluation_result["reason"],
        heart_rate=hr,
        latitude=payload.location.lat,
        longitude=payload.location.lng
    )

    db.add(event_log)
    db.commit()
    db.refresh(event_log)

    return evaluation_result