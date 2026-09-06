# Flood Monitoring Data Pipeline

A backend system for collecting, validating, storing, and serving water-distance data from ESP-based sensors.

This project is currently focused on **Pipeline 1: Sensor Data Logging** and the beginning of the **Panic Alert Pipeline**.

---

## 1. What This Project Does

The system receives sensor readings from an ESP device.

The current sensor gives a **distance measurement in centimeters**.

For example:

```text
[113.52]
```

This means the sensor measured a distance of `113.52 cm`.

The backend:

1. Receives the sensor data.
2. Identifies which ESP sent it using `device_id`.
3. Validates the sensor array.
4. Converts the reading into structured data.
5. Saves the data into SQLite.
6. Saves a human-readable copy into a JSON log.
7. Provides API endpoints to view the data.
8. Accepts an AI risk result for the panic pipeline.
9. Shows an emergency alert webpage when the AI reports `CRITICAL`.

---

# 2. Current System Architecture

```text
                    REAL WORLD
                        |
                        v
                +---------------+
                | ESP Sensor     |
                | Water Distance |
                +-------+-------+
                        |
                        | sensor reading
                        v
                +---------------+
                | Data Transport |
                | Wi-Fi / HTTP   |
                +-------+-------+
                        |
                        v
                +----------------------+
                | FastAPI Backend      |
                |                      |
                | /api/sensor-data     |
                +----------+-----------+
                           |
                           v
                     +-----------+
                     | parser.py |
                     +-----+-----+
                           |
                           v
                 +-------------------+
                 | database.py       |
                 +---------+---------+
                           |
                    +------+------+
                    |             |
                    v             v
              SQLite DB       JSON Log
                    |             |
                    +------+------+
                           |
                           v
                    AI Data Feed
                    (ai_feed.py)
                           |
                           v
                       AI Model
                           |
                           v
                    AI Risk Result
                           |
                           v
                    +-------------+
                    | panic.py    |
                    +------+------+ 
                           |
                    risk = CRITICAL
                           |
                           v
                    +-------------+
                    | Alert Page  |
                    | /alert      |
                    +-------------+
                           |
                    +------+------+
                    |             |
                    v             v
                  Laptop        Phone
```

---

# 3. Project Structure

The project is organized approximately like this:

```text
sih_pipeline/
│
├── .venv/
│   └── Python virtual environment
│
├── backend/
│   │
│   ├── __init__.py
│   │
│   ├── main.py
│   │   FastAPI application and API routes
│   │
│   ├── parser.py
│   │   Validates and converts ESP sensor arrays
│   │
│   ├── database.py
│   │   Handles SQLite and JSON storage
│   │
│   ├── panic.py
│   │   Handles AI risk results and emergency alerts
│   │
│   └── data/
│       ├── sensor_data.db
│       │   SQLite database
│       │
│       └── sensor_log.json
│           Human-readable sensor log
│
├── fake_esp.py
│   Simulates an ESP device for testing
│
├── ai_feed.py
│   Reads stored sensor data and prepares it for AI
│
├── serial_bridge.py
│   Optional local bridge for Arduino/ESP Serial testing
│
└── README.md
```

`__pycache__` folders and other temporary files may also appear. They are not part of the actual application logic.

---

# 4. Technologies Used

## Python

Python is used for the backend, data processing, testing scripts, and AI data pipeline.

## FastAPI

FastAPI provides the HTTP API.

The ESP or other programs can send data to FastAPI using HTTP requests.

## Uvicorn

Uvicorn runs the FastAPI application as a web server.

## SQLite

SQLite stores sensor readings in a local database file.

It is useful because it does not require a separate database server.

## JSON

JSON is used as a simple, readable log format.

## Requests

The `requests` Python package is used by the fake ESP and can also be used by other Python clients to send HTTP data.

---

# 5. Important Concept: ESP Data Format

The current design assumes:

**One ESP = one sensor = one distance value.**

Therefore, the ESP sends an array containing one value.

Example:

```json
[113.52]
```

For multiple ESP devices, every device has a unique ID.

Example:

```json
{
    "device_id": "ESP001",
    "data": [113.52]
}
```

Another device could send:

```json
{
    "device_id": "ESP002",
    "data": [97.25]
}
```

This allows the backend to know which sensor produced each reading.

---

# 6. Why We Store `distance_cm`

The backend currently stores the raw distance measured by the sensor.

Example:

```text
distance_cm = 113.52
```

We are intentionally **not converting this directly into `water_level_cm` yet**.

Why?

Because the actual sensor mounting/reference height has not been finalized.

A distance sensor measures the distance between the sensor and the water surface.

For example:

```text
Sensor
  |
  | 113.52 cm
  |
  v
Water Surface
```

To calculate actual water level, the fixed reference height of the sensor must be known.

Until that hardware value is finalized, storing the raw distance is safer and more accurate.

---

# 7. `parser.py`

The parser receives the sensor array.

Example:

```python
[113.52]
```

It checks:

- Is the input actually a list?
- Does it contain exactly one sensor value?
- Is the value numeric?
- Is the distance non-negative?

After validation, it creates structured data:

```python
{
    "device_id": "ESP001",
    "distance_cm": 113.52
}
```

The parser acts as a validation layer between incoming data and the database.

---

# 8. `database.py`

This file is responsible for storage.

It creates:

```text
backend/data/sensor_data.db
```

and:

```text
backend/data/sensor_log.json
```

## SQLite

The SQLite table contains:

```text
id
device_id
distance_cm
received_at
```

Example:

```text
1 | ESP001 | 113.52 | 2026-09-05T...
2 | ESP001 | 112.87 | 2026-09-05T...
```

The database is useful for structured querying and future analysis.

## JSON Log

The same readings are also written to:

```text
backend/data/sensor_log.json
```

Example:

```json
[
    {
        "device_id": "ESP001",
        "distance_cm": 113.52,
        "received_at": "2026-09-05T..."
    }
]
```

The JSON file is easy for developers and the AI pipeline to read.

---

# 9. `main.py`

`main.py` is the main FastAPI application.

It connects the different parts:

```text
API
 |
 +--> parser.py
 |
 +--> database.py
 |
 +--> panic.py
```

It also defines the URLs/endpoints.

---

# 10. API Endpoints

## Home

```http
GET /
```

URL:

```text
http://127.0.0.1:8000/
```

or from another device on the same network:

```text
http://10.65.238.131:8000/
```

It confirms that the backend is running.

Expected response:

```json
{
    "status": "online",
    "message": "Flood Monitoring Backend",
    "pipeline": "Data Logging"
}
```

---

# 11. Sensor Data Endpoint

```http
POST /api/sensor-data
```

Full local URL:

```text
http://127.0.0.1:8000/api/sensor-data
```

LAN URL:

```text
http://10.65.238.131:8000/api/sensor-data
```

Expected request:

```json
{
    "device_id": "ESP001",
    "data": [113.52]
}
```

The flow is:

```text
Incoming JSON
     |
     v
main.py
     |
     v
parser.py
     |
     v
Validated data
     |
     v
database.py
     |
     +----> SQLite
     |
     +----> JSON
```

---

# 12. Log Endpoint

```http
GET /api/logs
```

Local:

```text
http://127.0.0.1:8000/api/logs
```

LAN:

```text
http://10.65.238.131:8000/api/logs
```

It returns stored sensor readings.

Example:

```json
{
    "count": 2,
    "logs": [
        {
            "id": 2,
            "device_id": "ESP001",
            "distance_cm": 112.87,
            "received_at": "..."
        },
        {
            "id": 1,
            "device_id": "ESP001",
            "distance_cm": 113.52,
            "received_at": "..."
        }
    ]
}
```

---

# 13. Swagger API Documentation

FastAPI automatically provides an interactive API documentation page.

Open:

```text
http://127.0.0.1:8000/docs
```

From another device on the same network:

```text
http://10.65.238.131:8000/docs
```

Swagger allows you to test the API without writing a separate frontend.

For example:

1. Open `/docs`.
2. Find `POST /api/sensor-data`.
3. Click `Try it out`.
4. Enter JSON.
5. Click `Execute`.
6. Check the response.

---

# 14. `fake_esp.py`

`fake_esp.py` simulates a real ESP.

It generates a random distance value.

Example:

```text
Device: ESP001
Distance: 103.42 cm
Sending:
{
    "device_id": "ESP001",
    "data": [103.42]
}
```

It then sends the data to:

```text
http://127.0.0.1:8000/api/sensor-data
```

This is useful before the real hardware is ready.

## Important

`fake_esp.py` is only a testing tool.

It does not replace the real ESP.

---

# 15. How to Start the Project

Open PowerShell.

Go to the project:

```powershell
cd C:\Users\surya\Desktop\sih_pipeline
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should see something similar to:

```text
(.venv) PS C:\Users\surya\Desktop\sih_pipeline>
```

---

# 16. Start FastAPI

Run:

```powershell
uvicorn backend.main:app --reload
```

For local testing, this is enough.

The server will normally be available at:

```text
http://127.0.0.1:8000
```

Open it in your browser.

---

# 17. Start the Server for Phone/LAN Access

If you want another device, such as your phone, to connect to the laptop, run:

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The important part is:

```text
--host 0.0.0.0
```

This tells Uvicorn to listen on the laptop's network interfaces instead of only accepting connections from the laptop itself.

---

# 18. Laptop IP Address

The current laptop IPv4 address is:

```text
10.65.238.131
```

Therefore, the backend can be accessed from another device on the same network using:

```text
http://10.65.238.131:8000
```

Swagger:

```text
http://10.65.238.131:8000/docs
```

Logs:

```text
http://10.65.238.131:8000/api/logs
```

Alert page:

```text
http://10.65.238.131:8000/alert
```

---

# 19. How to Connect a Phone

The phone and laptop should be connected to the same Wi-Fi/network.

Then open the phone browser and enter:

```text
http://10.65.238.131:8000
```

If the connection works, the phone should show:

```json
{
    "status": "online",
    "message": "Flood Monitoring Backend",
    "pipeline": "Data Logging"
}
```

Then the phone can open:

```text
http://10.65.238.131:8000/alert
```

---

# 20. Important Difference: `127.0.0.1` vs Laptop IP

This is very important.

## `127.0.0.1`

Means:

> This same device.

If your laptop sends a request to:

```text
http://127.0.0.1:8000
```

it means the laptop itself.

If your phone opens:

```text
http://127.0.0.1:8000
```

the phone looks for a server running on the phone.

It does **not** mean your laptop.

## `10.65.238.131`

Means the laptop's address on the local network.

Therefore:

```text
Phone
  |
  | Wi-Fi
  v
10.65.238.131:8000
  |
  v
Laptop FastAPI
```

---

# 21. If Phone Cannot Connect

Check these things:

### 1. Same network

Make sure the phone and laptop are connected to the same Wi-Fi/network.

### 2. Correct Uvicorn command

Use:

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Correct IP

Check the laptop's IP with:

```powershell
ipconfig
```

Look for:

```text
IPv4 Address
```

The IP can change when the network changes.

### 4. Windows Firewall

Windows Firewall may block incoming connections to port `8000`.

If the laptop works but the phone cannot connect, firewall/network isolation is one of the first things to check.

Some guest Wi-Fi networks also prevent devices from communicating with each other.

---

# 22. AI Data Feed

The AI pipeline reads the existing sensor log.

The architecture is:

```text
ESP
 |
 v
FastAPI
 |
 v
sensor_log.json
 |
 v
ai_feed.py
 |
 v
AI model
```

This avoids creating a second independent logging system.

`ai_feed.py` reads:

```text
backend/data/sensor_log.json
```

and extracts readings for a particular device.

Example:

```text
ESP001
 |
 +--> 113.52
 +--> 112.87
 +--> 111.94
 +--> 110.72
```

These values can then be passed to the AI model.

---

# 23. Panic Pipeline

The panic pipeline begins after the AI produces a risk result.

The current architecture is:

```text
Sensor
   |
   v
Data Logger
   |
   v
AI Feed
   |
   v
AI Model
   |
   | risk_level
   v
panic.py
   |
   | CRITICAL
   v
FastAPI Alert System
   |
   v
/alert webpage
```

The AI can return something like:

```json
{
    "device_id": "ESP001",
    "risk_level": "CRITICAL",
    "distance_cm": 42.5
}
```

The panic system checks:

```text
risk_level == "CRITICAL"
```

If true, an emergency alert is created.

---

# 24. Panic API

Endpoint:

```http
POST /api/panic
```

LAN URL:

```text
http://10.65.238.131:8000/api/panic
```

Example input:

```json
{
    "device_id": "ESP001",
    "risk_level": "CRITICAL",
    "distance_cm": 42.5
}
```

Expected result:

```json
{
    "alert": true,
    "type": "PANIC",
    "device_id": "ESP001",
    "risk_level": "CRITICAL",
    "distance_cm": 42.5,
    "message": "EMERGENCY FLOOD ALERT"
}
```

---

# 25. Alert Webpage

Open:

```text
http://10.65.238.131:8000/alert
```

Before an emergency, it shows:

```text
🟢 FLOOD MONITORING SYSTEM

No Emergency Detected
```

After a `CRITICAL` AI result, it shows an emergency alert.

The current prototype stores the latest alert in server memory.

That means:

**If the FastAPI server restarts, the current alert state resets.**

This is acceptable for the current prototype but should be improved for a production system.

---

# 26. Complete Testing Procedure

Use this order when testing the entire project.

## Step 1 — Open PowerShell

```powershell
cd C:\Users\surya\Desktop\sih_pipeline
```

## Step 2 — Activate environment

```powershell
.\.venv\Scripts\Activate.ps1
```

## Step 3 — Start backend

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Keep this terminal running.

---

## Step 4 — Test home page

Open:

```text
http://127.0.0.1:8000/
```

or:

```text
http://10.65.238.131:8000/
```

---

## Step 5 — Open Swagger

```text
http://127.0.0.1:8000/docs
```

Test:

```text
POST /api/sensor-data
```

with:

```json
{
    "device_id": "ESP001",
    "data": [113.52]
}
```

---

## Step 6 — Check logs

Open:

```text
http://127.0.0.1:8000/api/logs
```

You should see the new reading.

Also check:

```text
backend/data/sensor_log.json
```

---

## Step 7 — Test Fake ESP

Open a second PowerShell terminal.

Go to the project:

```powershell
cd C:\Users\surya\Desktop\sih_pipeline
```

Activate the environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Run:

```powershell
python fake_esp.py
```

The fake ESP will repeatedly send sensor readings.

---

## Step 8 — Test AI feed

Run:

```powershell
python ai_feed.py
```

It should read the stored sensor data.

---

## Step 9 — Test Panic Pipeline

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Find:

```text
POST /api/panic
```

Send:

```json
{
    "device_id": "ESP001",
    "risk_level": "CRITICAL",
    "distance_cm": 42.5
}
```

---

## Step 10 — Open Alert Page

Refresh:

```text
http://127.0.0.1:8000/alert
```

The emergency alert should appear.

From the phone, use:

```text
http://10.65.238.131:8000/alert
```

provided the phone and laptop are on the same network.

---

# 27. Real Hardware Integration

When the real ESP is ready, the fake ESP is no longer required.

The desired final flow is:

```text
REAL ESP
   |
   | Wi-Fi / HTTP
   v
FastAPI
   |
   v
/api/sensor-data
```

The ESP should send:

```json
{
    "device_id": "ESP001",
    "data": [113.52]
}
```

The backend does not care whether the sender is:

- a real ESP,
- a fake Python ESP,
- another computer,
- or another compatible client.

As long as it sends the correct API request.

---

# 28. Serial Bridge

During hardware testing, the Arduino/ESP may output something like:

```text
Distance: 113.52 cm
```

A temporary Python `serial_bridge.py` can read this Serial output, extract the number, convert it into:

```text
[113.52]
```

and send it to the FastAPI endpoint.

This gives:

```text
Arduino/ESP
    |
    | USB Serial
    v
serial_bridge.py
    |
    | HTTP
    v
FastAPI
```

This is mainly a development/testing bridge.

If the final ESP sends data directly through Wi-Fi, the bridge is not necessary.

---

# 29. Multiple ESP Devices

The backend supports multiple devices by using `device_id`.

Example:

```text
ESP001
ESP002
ESP003
ESP004
```

Each device sends:

```json
{
    "device_id": "ESP002",
    "data": [97.25]
}
```

The backend can therefore distinguish readings:

```text
ESP001 -> 113.52 cm
ESP002 -> 97.25 cm
ESP003 -> 105.81 cm
```

This becomes important when deploying sensors at multiple locations.

---

# 30. Why We Have Separate Files

Each file has one main responsibility.

```text
main.py
    |
    +--> API / server

parser.py
    |
    +--> validation / conversion

database.py
    |
    +--> storage

panic.py
    |
    +--> emergency decision handling

fake_esp.py
    |
    +--> testing sensor

ai_feed.py
    |
    +--> AI input preparation

serial_bridge.py
    |
    +--> optional hardware Serial bridge
```

This separation makes the project easier to understand, test, and expand.

---

# 31. Current Limitations

This is currently a prototype/development system.

Important limitations:

1. The alert state is stored in memory.
2. The alert webpage does not automatically update in real time yet.
3. No real government API has been connected.
4. Sensor mounting height has not yet been finalized.
5. `water_level_cm` is therefore not calculated yet.
6. Authentication has not been implemented.
7. The local development server uses HTTP rather than production HTTPS.
8. The laptop's local IP may change.
9. The system is currently intended for a trusted development network.

---

# 32. Future Improvements

Possible next stages:

### Backend

- Add proper Pydantic request models.
- Add authentication for ESP devices.
- Add better error handling.
- Add database indexes.
- Add API logging.

### Sensor system

- Finalize sensor mounting height.
- Convert distance into water level.
- Add calibration.
- Support multiple sensor types if required.

### AI

- Create a defined AI input schema.
- Add time-series features.
- Add prediction confidence.
- Define risk levels such as:
  - NORMAL
  - WARNING
  - DANGER
  - CRITICAL

### Alert system

- Automatic webpage updates.
- WebSockets or polling.
- Persistent alert storage.
- Alert acknowledgement.
- Multiple recipients.
- SMS/email/push notification integration where appropriate.

### Deployment

- Deploy FastAPI on a proper server.
- Use HTTPS.
- Use a domain.
- Add authentication.
- Add monitoring and logging.

---

# 33. Developer Quick Reference

## Start project

```powershell
cd C:\Users\surya\Desktop\sih_pipeline
.\.venv\Scripts\Activate.ps1
```

## Start local server

```powershell
uvicorn backend.main:app --reload
```

## Start LAN server

```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## Run fake ESP

```powershell
python fake_esp.py
```

## Run AI feed

```powershell
python ai_feed.py
```

## Local URLs

```text
Home:
http://127.0.0.1:8000/

Swagger:
http://127.0.0.1:8000/docs

Logs:
http://127.0.0.1:8000/api/logs

Alert:
http://127.0.0.1:8000/alert
```

## LAN URLs

```text
Home:
http://10.65.238.131:8000/

Swagger:
http://10.65.238.131:8000/docs

Logs:
http://10.65.238.131:8000/api/logs

Alert:
http://10.65.238.131:8000/alert
```

---

# 34. One-Line Summary

The project takes raw distance readings from ESP sensors, sends them to a FastAPI backend, validates and stores them in SQLite/JSON, feeds the stored data toward the AI system, and converts a `CRITICAL` AI result into an emergency alert that can be viewed from the laptop or another device on the same network.

---

## Project Status

**Current stage:** Prototype / Development

**Completed:**

- FastAPI backend
- Sensor data API
- Sensor array parser
- SQLite storage
- JSON logging
- Fake ESP testing
- AI data feed foundation
- Panic pipeline
- Alert webpage
- LAN access from phone/laptop

**Next major stage:**

Real ESP → FastAPI → persistent data → AI model → real-time alert system
