import serial
import requests
import time


# ========================================
# ARDUINO SETTINGS
# ========================================

SERIAL_PORT = "COM5"   # CHANGE THIS
BAUD_RATE = 9600


# ========================================
# BACKEND API
# ========================================

API_URL = (
    "http://127.0.0.1:8000/api/sensor-data"
)


# ========================================
# DEVICE ID
# ========================================

DEVICE_ID = "ESP001"


# ========================================
# CONNECT TO ARDUINO
# ========================================

arduino = serial.Serial(
    SERIAL_PORT,
    BAUD_RATE,
    timeout=1
)

time.sleep(2)


print("===================================")
print("      ARDUINO DATA BRIDGE")
print("===================================")

print(
    f"Connected to {SERIAL_PORT}"
)

print(
    "Waiting for sensor data..."
)


# ========================================
# READ ARDUINO DATA
# ========================================

while True:

    try:

        line = arduino.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()


        if not line:
            continue


        print(
            "Arduino:",
            line
        )


        # --------------------------------
        # LOOK FOR DISTANCE
        # --------------------------------

        if line.startswith("Distance:"):

            # Example:
            #
            # Distance: 100.17 cm
            #
            # We need:
            #
            # 100.17

            value = (
                line
                .replace("Distance:", "")
                .replace("cm", "")
                .strip()
            )


            distance = float(value)


            # --------------------------------
            # CREATE API PAYLOAD
            # --------------------------------

            payload = {

                "device_id":
                    DEVICE_ID,

                "data": [
                    distance
                ]

            }


            print(
                "Sending to backend:",
                payload
            )


            # --------------------------------
            # SEND TO FASTAPI
            # --------------------------------

            response = requests.post(

                API_URL,

                json=payload,

                timeout=5

            )


            print(
                "Server:",
                response.json()
            )


    except ValueError:

        print(
            "Could not read distance value."
        )


    except requests.exceptions.RequestException as error:

        print(
            "Backend connection error:",
            error
        )


    except KeyboardInterrupt:

        print(
            "\nBridge stopped."
        )

        break