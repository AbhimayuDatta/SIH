import requests
import time
import random


# ========================================
# BACKEND
# ========================================

API_URL = (
    "http://127.0.0.1:8000/api/sensor-data"
)


# ========================================
# ESP INFORMATION
# ========================================

DEVICE_ID = "ESP001"


# ========================================
# START
# ========================================

print("===================================")
print("       FAKE ESP001 STARTED")
print("===================================")


while True:

    # -------------------------------
    # ONE SENSOR READING
    # -------------------------------

    distance = round(
        random.uniform(75, 120),
        2
    )


    # ESP sends an array

    sensor_array = [
        distance
    ]


    # -------------------------------
    # PAYLOAD
    # -------------------------------

    payload = {

        "device_id":
            DEVICE_ID,

        "data":
            sensor_array
    }


    print()
    print("-----------------------------------")

    print(
        f"Device: {DEVICE_ID}"
    )

    print(
        f"Distance: {distance} cm"
    )

    print(
        f"Sending: {payload}"
    )


    # -------------------------------
    # SEND TO SERVER
    # -------------------------------

    try:

        response = requests.post(

            API_URL,

            json=payload,

            timeout=5

        )


        print(
            "Server response:"
        )

        print(
            response.json()
        )


    except requests.exceptions.ConnectionError:

        print(
            "ERROR: Backend is not running."
        )


    except requests.exceptions.RequestException as error:

        print(
            "Request error:",
            error
        )


    # -------------------------------
    # WAIT
    # -------------------------------

    time.sleep(10)