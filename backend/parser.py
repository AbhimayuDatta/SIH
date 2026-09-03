def parse_sensor_array(data, device_id):
    """
    Convert ESP sensor array into structured data.

    Example input:
        [100.17]

    One ESP sends one sensor reading.
    """

    if not isinstance(data, list):
        raise ValueError("Sensor data must be an array")

    if len(data) != 1:
        raise ValueError(
            "Expected exactly one sensor value"
        )

    try:
        distance = float(data[0])
    except (TypeError, ValueError):
        raise ValueError(
            "Sensor distance must be a number"
        )

    if distance < 0:
        raise ValueError(
            "Sensor distance cannot be negative"
        )

    return {
        "device_id": device_id,
        "distance_cm": distance
    }