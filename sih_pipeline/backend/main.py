from fastapi import FastAPI, HTTPException, Body

from backend.parser import parse_sensor_array

from backend.database import (
    initialize_database,
    save_sensor_data,
    get_sensor_logs
)


app = FastAPI(
    title="Flood Monitoring Data Pipeline"
)


# Initialize database when the server starts
initialize_database()


@app.get("/")
def home():

    return {
        "status": "online",
        "message": "Flood Monitoring Backend"
    }


@app.post("/api/sensor-data")
def receive_sensor_data(data: list = Body(...)):

    try:

        # Convert ESP array into structured data
        sensor_data = parse_sensor_array(data)

        # Save data into database
        received_at = save_sensor_data(sensor_data)

        return {
            "status": "success",
            "message": "Sensor data logged",
            "data": {
                **sensor_data,
                "received_at": received_at
            }
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@app.get("/api/logs")
def get_logs(limit: int = 100):

    logs = get_sensor_logs(limit)

    return {
        "count": len(logs),
        "logs": logs
    }