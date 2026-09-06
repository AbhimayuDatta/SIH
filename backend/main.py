from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from backend.panic import panic_check
from backend.database import (
    initialize_database,
    save_sensor_data,
    get_sensor_logs
)

from fastapi import FastAPI, HTTPException

from backend.parser import parse_sensor_array
from backend.database import (
    initialize_database,
    save_sensor_data,
    get_sensor_logs
)




# ========================================
# FASTAPI APPLICATION
# ========================================

app = FastAPI(
    title="Flood Monitoring Data Pipeline",
    description="Pipeline 1 - Sensor Data Logging",
    version="1.0"
)
 #=======================================
 # Alert State
 #=======================================

current_alert = {
    "alert": False,
    "message": "No emergency detected"
}

# ========================================
# INITIALIZE DATABASE
# ========================================

initialize_database()


# ========================================
# HOME
# ========================================

@app.get("/")
def home():

    return {
        "status": "online",
        "message": "Flood Monitoring Backend",
        "pipeline": "Data Logging"
    }


# ========================================
# RECEIVE SENSOR DATA
# ========================================

@app.post("/api/sensor-data")
def receive_sensor_data(payload: dict):

    try:

        # -------------------------------
        # GET DEVICE ID
        # -------------------------------

        device_id = payload.get(
            "device_id"
        )

        if not device_id:

            raise ValueError(
                "device_id is required"
            )


        # -------------------------------
        # GET SENSOR ARRAY
        # -------------------------------

        data = payload.get(
            "data"
        )

        if data is None:

            raise ValueError(
                "data is required"
            )


        # -------------------------------
        # PARSE
        # -------------------------------

        sensor_data = parse_sensor_array(
            data,
            device_id
        )


        # -------------------------------
        # SAVE
        # -------------------------------

        received_at = save_sensor_data(
            sensor_data
        )


        # -------------------------------
        # RESPONSE
        # -------------------------------

        return {

            "status": "success",

            "message":
                "Sensor data logged successfully",

            "data": {

                **sensor_data,

                "received_at":
                    received_at
            }
        }


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# ========================================
# GET LOGS
# ========================================

@app.get("/api/logs")
def get_logs(limit: int = 100):

    logs = get_sensor_logs(
        limit
    )

    return {

        "count": len(logs),

        "logs": logs

    }

@app.post("/api/panic")
def receive_ai_result(ai_result: dict):
    global current_alert

    current_alert = panic_check(ai_result)

    return current_alert

@app.get("/alert", response_class=HTMLResponse)
def alert_page():

    if current_alert.get("alert") is True:

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>EMERGENCY FLOOD ALERT</title>

            <style>
                body {{
                    margin: 0;
                    font-family: Arial, sans-serif;
                    background: #8b0000;
                    color: white;
                    text-align: center;
                }}

                .alert {{
                    margin-top: 100px;
                    padding: 40px;
                }}

                h1 {{
                    font-size: 60px;
                }}

                h2 {{
                    font-size: 35px;
                }}

                .info {{
                    font-size: 22px;
                    margin: 15px;
                }}
            </style>
        </head>

        <body>

            <div class="alert">

                <h1>🚨</h1>

                <h1>EMERGENCY FLOOD ALERT</h1>

                <h2>CRITICAL CONDITION</h2>

                <div class="info">
                    Device: {current_alert.get("device_id")}
                </div>

                <div class="info">
                    Distance: {current_alert.get("distance_cm")} cm
                </div>

                <div class="info">
                    Time: {current_alert.get("time")}
                </div>

                <h2>IMMEDIATE ATTENTION REQUIRED</h2>

            </div>

        </body>
        </html>
        """

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flood Monitoring</title>
    </head>

    <body style="text-align:center; font-family:Arial; margin-top:100px;">

        <h1>🟢 FLOOD MONITORING SYSTEM</h1>

        <h2>No Emergency Detected</h2>

    </body>
    </html>
    """
   