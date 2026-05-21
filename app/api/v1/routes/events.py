from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.event_service import (
    get_all_events,
    get_alerts,
    get_device_events,
    get_summary_report
)

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def all_events(db: Session = Depends(get_db)):
    return get_all_events(db)


@router.get("/alerts", status_code=status.HTTP_200_OK)
def alerts(db: Session = Depends(get_db)):
    return get_alerts(db)


@router.get("/device/{device_id}", status_code=status.HTTP_200_OK)
def device_events(device_id: str, db: Session = Depends(get_db)):
    return get_device_events(db, device_id)


@router.get("/report/summary", status_code=status.HTTP_200_OK)
def summary(db: Session = Depends(get_db)):
    return get_summary_report(db)