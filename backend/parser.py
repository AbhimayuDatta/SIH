def parse_sensor_array(data: list) -> dict:

    if len(data) != 4:
        raise ValueError(
            "Invalid sensor data. Expected 4 values."
        )

    device_id = data[0]
    distance_cm = data[1]
    water_level_cm = data[2]
    rainfall_mm = data[3]

    if not isinstance(device_id, str):
        raise ValueError("Device ID must be a string.")

    return {
        "device_id": device_id,
        "distance_cm": float(distance_cm),
        "water_level_cm": float(water_level_cm),
        "rainfall_mm": float(rainfall_mm)
    }