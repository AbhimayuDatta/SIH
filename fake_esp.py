import requests
import random
import time


SERVER_URL = "http://127.0.0.1:8000/api/sensor-data"

DEVICE_ID = "ESP001"


def generate_sensor_data():

    distance_cm = round(
        random.uniform(100, 120),
        2
    )

    water_level_cm = round(
        200 - distance_cm,
        2
    )

    rainfall_mm = round(
        random.uniform(0, 10),
        2
    )

    return [
        DEVICE_ID,
        distance_cm,
        water_level_cm,
        rainfall_mm
    ]


def send_data():

    sensor_data = generate_sensor_data()

    print("\nSending sensor data:")
    print(sensor_data)

    try:

        response = requests.post(
            SERVER_URL,
            json=sensor_data,
            timeout=5
        )

        print("Server response:")
        print(response.json())

    except requests.exceptions.RequestException as error:

        print("Could not connect to server:")
        print(error)


if __name__ == "__main__":

    while True:

        send_data()

        time.sleep(10)