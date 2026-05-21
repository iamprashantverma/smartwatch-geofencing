# Smartwatch Geofencing API

FastAPI service for ingesting smartwatch telemetry, detecting geofence transitions, evaluating health/location events, and storing both raw device readings and alert records in MySQL.

**Design reference:**  — architecture diagram, API reference, assumptions, and scaling approach.

## Architecture Diagram
<img width="1693" height="929" alt="ChatGPT Image May 21, 2026, 05_43_58 PM" src="https://github.com/user-attachments/assets/6b883088-6004-4352-86ac-659a0e8ad4ed" />

## What This Project Does

1. A smartwatch or simulator sends heart rate, steps, timestamp, and GPS coordinates.
2. The API detects the current geofence using configured zone centers and radii.
3. The latest stored reading for the device is used to classify movement as `ENTRY`, `EXIT`, `STAY`, or `OUTSIDE`.
4. Rule-based event evaluation assigns event name, severity, status, and reason.
5. Raw telemetry and evaluated events are stored in MySQL.
6. Optional Ollama integration can generate a concise AI explanation for each event.

## Project Structure

- `app/main.py` creates the FastAPI application and registers API routes.
- `app/api/v1/routes/ingest.py` exposes telemetry ingestion.
- `app/api/v1/routes/devices.py` exposes device data, event, alert, and summary endpoints.
- `app/services/geofence_service.py` detects the active geofence and movement event type.
- `app/services/ingestion_service.py` stores raw device data and triggers event evaluation.
- `app/services/event_service.py` evaluates events and serves event reporting queries.
- `app/services/ai_service_evaluation.py` optionally calls Ollama for alert explanations.
- `app/geofencing/geofences.py` contains the static geofence definitions.
- `simulator/simple_simulator.py` sends sample telemetry to the ingestion endpoint.

## Requirements

Install or prepare these before running the project:

- Python 3.11 or newer
- MySQL server
- A MySQL database for this service
- `pip`
- Optional: Ollama, only if `AI_EXPLANATION=true`

Python packages are listed in `requirements.txt`. Main packages include:

- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- PyMySQL
- Pydantic
- Geopy
- Requests

## How To Run

Follow these steps from the project root.

### 1. Create Virtual Environment

Windows PowerShell:

```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
copy .env.example .env
```

Update `.env` with your local database details:

```env
DATABASE_URL=mysql+pymysql://USER:PASSWORD@localhost:3306/DB_NAME
OLLAMA_BASE_MODEL=qwen2.5:7b
OLLAMA_BASE_URL=http://localhost:11434
AI_EXPLANATION=false
```

Environment variables:

| Variable | Required | Description |
| --- | --- | --- |
| `DATABASE_URL` | Yes | SQLAlchemy database URL for MySQL. |
| `OLLAMA_BASE_MODEL` | Yes | Ollama model name used when AI explanations are enabled. |
| `OLLAMA_BASE_URL` | Yes | Ollama server URL. |
| `AI_EXPLANATION` | Yes | Set `true` to generate AI explanations, otherwise `false`. |

### 4. Create Database

Create the MySQL database referenced in `DATABASE_URL` before running migrations.

Example:

```sql
CREATE DATABASE smartwatch_geofencing;
```

Then your `.env` can use:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/smartwatch_geofencing
```

### 5. Run Migrations

Alembic migrations create and update the database tables.

```bash
alembic upgrade head
```

Useful migration commands:

```bash
alembic current
alembic history
alembic upgrade head
```

### 6. Start API Server

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

### 7. Run Simulator

Open a second terminal, activate the same virtual environment, and run:

```bash
python simulator/simple_simulator.py
```

The simulator sends sample data for devices `DEV001` to `DEV005` every 10 seconds to:

```text
http://localhost:8000/ingest/
```

You should see logs like:

```text
DEV001: (28.614081, 77.208721) - Office Zone - ENTRY
DEV002: (28.616882, 77.214910) - Restricted Zone - STAY
```

Stop the simulator with `Ctrl+C`.

## Run Order Summary

Use this order when starting from a fresh setup:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Then in another terminal:

```bash
venv\Scripts\activate
python simulator/simple_simulator.py
```

## API Details

### Ingest Device Telemetry

`POST /ingest/`

Stores a smartwatch reading, detects the current zone, derives the geofence event type, evaluates the reading, and creates an event log.

Request body:

```json
{
  "device_id": "DEV001",
  "heart_rate": 118,
  "steps": 2450,
  "location": {
    "lat": 28.6139,
    "lng": 77.209
  },
  "timestamp": "2026-05-21T12:30:00Z"
}
```

Validation rules:

- `device_id`: 3 to 50 characters
- `heart_rate`: 30 to 220
- `steps`: 0 or greater
- `location.lat`: -90 to 90
- `location.lng`: -180 to 180
- `timestamp`: valid datetime

Successful response:

```json
{
  "status": "success",
  "message": "Device data stored successfully",
  "data": {
    "id": 1,
    "device_id": "DEV001",
    "zone": "Office Zone",
    "event_type": "ENTRY",
    "created_at": "2026-05-21T12:30:01"
  },
  "is_first_record": true
}
```

### Get All Device Data

`GET /devices/data`

Returns all raw device readings ordered by newest first.

### Get Device Data by Device ID

`GET /devices/{device_id}/data`

Returns raw readings for one device ordered by newest first.

Example:

```bash
curl http://localhost:8000/devices/DEV001/data
```

### Get All Events

`GET /devices/events`

Returns all evaluated event logs ordered by newest first.

### Get Alerts

`GET /devices/events/alerts`

Returns high-severity event logs.

### Get Device Events

`GET /devices/{device_id}/events`

Returns evaluated events for one device ordered by newest first.

### Get Summary Report

`GET /devices/events/report/summary`

Returns aggregate event counts and activity grouped by zone.

Example response:

```json
{
  "status": "success",
  "total_events": 25,
  "high_severity_events": 3,
  "zone_activity": {
    "Office Zone": 10,
    "Restricted Zone": 5,
    "Warehouse Zone": 4,
    "Research Lab Zone": 3,
    "Parking Zone": 3
  }
}
```

## Event Evaluation Rules

The system uses deterministic rules to classify events from zone, heart rate, steps, and movement event type.

Examples:

- Heart rate above 140 inside a zone creates an emergency heart-rate event.
- Heart rate above 120 inside `Restricted Zone` creates a high-risk restricted-zone alert.
- Entry into `Restricted Zone` creates a flagged restricted-zone entry event.
- Steps above 10000 inside `Research Lab Zone` creates an unusual high-activity event.
- Low steps inside `Warehouse Zone` creates a low-activity monitoring event.
- Entry into `Parking Zone` creates an informational event.

## Geofence Configuration

Current static geofences are defined in `app/geofencing/geofences.py`:

| Zone | Latitude | Longitude | Radius |
| --- | ---: | ---: | ---: |
| Office Zone | 28.6139 | 77.2090 | 300 m |
| Restricted Zone | 28.6170 | 77.2150 | 200 m |
| Warehouse Zone | 28.6085 | 77.2030 | 250 m |
| Research Lab Zone | 28.6200 | 77.2050 | 220 m |
| Parking Zone | 28.6050 | 77.2125 | 180 m |

## Assumptions

- Devices send trusted telemetry in the expected JSON shape.
- Device identity is represented by `device_id`; there is no authentication or device registry yet.
- Geofences are circular and configured statically in code.
- Latitude and longitude are evaluated using geodesic distance in meters.
- The latest stored reading for a device is the source of truth for detecting transitions.
- MySQL is available and migrations are applied before running the API.
- AI explanations are optional and require a reachable Ollama server when `AI_EXPLANATION=true`.
- Timestamps are accepted from the request, while database records use server-created timestamps.
- The current service is optimized for a prototype or internal monitoring workflow, not direct public internet exposure.

## Scaling Approach

For more devices, higher ingestion volume, or production use, evolve the design in stages:

1. Move ingestion to an asynchronous pipeline.
   - Accept telemetry quickly through the API.
   - Publish readings to Kafka, RabbitMQ, Redis Streams, or a cloud queue.
   - Process geofence detection and event evaluation in workers.

2. Store geofences in the database.
   - Replace static Python geofence definitions with CRUD-managed zone records.
   - Add spatial indexes if using a database with geospatial support.
   - Cache active geofences in Redis for fast lookups.

3. Improve query performance.
   - Add indexes for `device_id`, `created_at`, `severity`, `zone`, and common report filters.
   - Paginate `/devices/data`, `/devices/events`, and per-device history endpoints.
   - Partition or archive old telemetry when the table grows large.

4. Separate raw telemetry from event analytics.
   - Keep raw telemetry in a write-optimized store or time-series database.
   - Keep event logs in relational storage for reporting and audit workflows.
   - Send aggregate metrics to a monitoring or analytics backend.

5. Scale the API horizontally.
   - Run multiple FastAPI workers behind a load balancer.
   - Keep application instances stateless.
   - Use shared database, cache, and queue infrastructure.

