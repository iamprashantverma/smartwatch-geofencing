from sqlalchemy import Column, Integer, Float, String, DateTime, func

from app.db.base import Base


class DeviceData(Base):
    __tablename__ = "device_data"

    id = Column(Integer, primary_key=True, index=True)

    device_id = Column(String(50), nullable=False, index=True)
    heart_rate = Column(Integer, nullable=False)
    steps = Column(Integer, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    zone = Column(String(50), nullable=True)
    event_type = Column(String(20), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())