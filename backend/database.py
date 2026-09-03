import sqlite3
import json

from pathlib import Path
from datetime import datetime, timezone


# ========================================
# FILE LOCATIONS
# ========================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"

DATABASE_FILE = DATA_DIR / "sensor_data.db"

JSON_FILE = DATA_DIR / "sensor_log.json"


# ========================================
# INITIALIZE DATABASE
# ========================================

def initialize_database():

    # Create data folder if it doesn't exist

    DATA_DIR.mkdir(
        exist_ok=True
    )

    # Create SQLite database

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensor_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            device_id TEXT NOT NULL,

            distance_cm REAL NOT NULL,

            received_at TEXT NOT NULL

        )
    """)

    connection.commit()

    connection.close()


    # Create JSON file

    if not JSON_FILE.exists():

        with open(
            JSON_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                [],
                file,
                indent=4
            )


# ========================================
# SAVE SENSOR DATA
# ========================================

def save_sensor_data(sensor_data):

    received_at = datetime.now(
        timezone.utc
    ).isoformat()


    # ====================================
    # SAVE TO SQLITE
    # ====================================

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO sensor_logs (
            device_id,
            distance_cm,
            received_at
        )
        VALUES (?, ?, ?)
    """, (
        sensor_data["device_id"],
        sensor_data["distance_cm"],
        received_at
    ))

    connection.commit()

    connection.close()


    # ====================================
    # SAVE TO JSON
    # ====================================

    try:

        with open(
            JSON_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            logs = json.load(file)

    except (
        FileNotFoundError,
        json.JSONDecodeError
    ):

        logs = []


    new_log = {
        "device_id":
            sensor_data["device_id"],

        "distance_cm":
            sensor_data["distance_cm"],

        "received_at":
            received_at
    }


    logs.append(new_log)


    with open(
        JSON_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            logs,
            file,
            indent=4
        )


    return received_at


# ========================================
# GET SENSOR LOGS
# ========================================

def get_sensor_logs(limit=100):

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            device_id,
            distance_cm,
            received_at

        FROM sensor_logs

        ORDER BY id DESC

        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    connection.close()

    return [
        dict(row)
        for row in rows
    ]