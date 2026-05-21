from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.device_data_service import (
    get_all_device_data,
    get_device_data_by_id
)
from app.services.event_service import (
    get_all_events,
    get_alerts,
    get_device_events,
    get_summary_report
)

router = APIRouter()


@router.get("/data", status_code=status.HTTP_200_OK)
def all_device_data(db: Session = Depends(get_db)):
    return get_all_device_data(db)


@router.get("/{device_id}/data", status_code=status.HTTP_200_OK)
def device_data_by_id(device_id: str, db: Session = Depends(get_db)):
    """Get all data records for a specific device"""
    return get_device_data_by_id(db, device_id)


@router.get("/events", status_code=status.HTTP_200_OK)
def all_events(db: Session = Depends(get_db)):
    """Get all events from all devices"""
    return get_all_events(db)


@router.get("/events/alerts", status_code=status.HTTP_200_OK)
def alerts(db: Session = Depends(get_db)):
    return get_alerts(db)


@router.get("/{device_id}/events", status_code=status.HTTP_200_OK)
def device_events(device_id: str, db: Session = Depends(get_db)):
    return get_device_events(db, device_id)


@router.get("/events/report/summary", status_code=status.HTTP_200_OK)
def summary(db: Session = Depends(get_db)):
    return get_summary_report(db)
