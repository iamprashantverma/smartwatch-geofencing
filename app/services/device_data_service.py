from sqlalchemy.orm import Session

from app.models.device_data import DeviceData


def get_all_device_data(db: Session):
    device_data = (
        db.query(DeviceData)
        .order_by(DeviceData.created_at.desc())
        .all()
    )

    return {
        "status": "success",
        "count": len(device_data),
        "data": device_data
    }


def get_device_data_by_id(db: Session, device_id: str):

    device_data = (
        db.query(DeviceData)
        .filter(DeviceData.device_id == device_id)
        .order_by(DeviceData.created_at.desc())
        .all()
    )

    return {
        "status": "success",
        "device_id": device_id,
        "count": len(device_data),
        "data": device_data
    }
