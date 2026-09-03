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