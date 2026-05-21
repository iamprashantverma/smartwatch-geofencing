import random
import time
import requests
from datetime import datetime, timezone
import math

GEOFENCES = [
    {"name": "Office Zone", "latitude": 28.6139, "longitude": 77.2090, "radius": 300},
    {"name": "Restricted Zone", "latitude": 28.6170, "longitude": 77.2150, "radius": 200},
    {"name": "Warehouse Zone", "latitude": 28.6085, "longitude": 77.2030, "radius": 250},
    {"name": "Research Lab Zone", "latitude": 28.6200, "longitude": 77.2050, "radius": 220},
    {"name": "Parking Zone", "latitude": 28.6050, "longitude": 77.2125, "radius": 180}
]

DEVICES = {}

def move_position(lat, lng, distance_meters=50):
    angle = random.uniform(0, 2 * math.pi)
    lat_change = (distance_meters / 111111.0) * math.sin(angle)
    lng_change = (distance_meters / (111111.0 * math.cos(math.radians(lat)))) * math.cos(angle)
    return round(lat + lat_change, 6), round(lng + lng_change, 6)

def init_device(device_id):
    zone = random.choice(GEOFENCES)
    inside = random.random() < 0.7
    
    if inside:
        distance = random.uniform(0, zone["radius"] * 0.8)
    else:
        distance = random.uniform(zone["radius"] * 1.2, zone["radius"] * 2)
    
    angle = random.uniform(0, 2 * math.pi)
    lat = zone["latitude"] + (distance / 111111.0) * math.sin(angle)
    lng = zone["longitude"] + (distance / (111111.0 * math.cos(math.radians(zone["latitude"])))) * math.cos(angle)
    
    DEVICES[device_id] = {
        "lat": round(lat, 6),
        "lng": round(lng, 6),
        "steps": random.randint(0, 5000)
    }

def generate_data(device_id):
    if device_id not in DEVICES:
        init_device(device_id)
    
    device = DEVICES[device_id]
    
    if random.random() < 0.1:
        device["lat"], device["lng"] = move_position(device["lat"], device["lng"], random.randint(100, 300))
    else:
        device["lat"], device["lng"] = move_position(device["lat"], device["lng"], random.randint(10, 80))
    
    device["steps"] += random.randint(10, 100)
    
    return {
        "device_id": device_id,
        "heart_rate": random.randint(60, 150),
        "steps": device["steps"],
        "location": {
            "lat": device["lat"],
            "lng": device["lng"]
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def run():
    device_ids = ["DEV001", "DEV002", "DEV003", "DEV004", "DEV005"]
    url = "http://localhost:8000/ingest/"
    
    print("Starting simulator...")
    
    try:
        while True:
            for device_id in device_ids:
                data = generate_data(device_id)
                try:
                    response = requests.post(url, json=data, timeout=5)
                    if response.status_code in [200, 201]:
                        result = response.json()
                        event = result.get("data", {}).get("event_type", "None")
                        zone = result.get("data", {}).get("zone", "Unknown")
                        print(f"{device_id}: ({data['location']['lat']}, {data['location']['lng']}) - {zone} - {event}")
                    else:
                        print(f"{device_id}: Error {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"{device_id}: Connection Error - {e}")
            
            print("-" * 60)
            time.sleep(10)
    
    except KeyboardInterrupt:
        print("\nStopped")

if __name__ == "__main__":
    run()
