from geopy.distance import geodesic
from typing import Optional

from app.geofencing.geofences import GEOFENCES
from app.core.constants import ZoneEvent


def detect_zone(latitude: float, longitude: float) -> Optional[str]:
    device_location = (latitude, longitude)

    for zone in GEOFENCES:
        zone_center = (zone["latitude"], zone["longitude"])

        distance = geodesic(device_location, zone_center).meters

        if distance <= zone["radius"]:
            return zone["name"]

    return None


def detect_zone_event(previous_zone: Optional[str], current_zone: Optional[str]) -> Optional[ZoneEvent]:

    # Entered a zone
    if previous_zone is None and current_zone is not None:
        return ZoneEvent.ENTRY

    # Exited a zone
    if previous_zone is not None and current_zone is None:
        return ZoneEvent.EXIT

    # Still inside same zone
    if previous_zone == current_zone and current_zone is not None:
        return ZoneEvent.STAY

    # Moved between zones (optional future case)
    if previous_zone != current_zone and current_zone is not None:
        return ZoneEvent.ENTRY

    return None