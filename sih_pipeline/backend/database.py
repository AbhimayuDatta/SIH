import sqlite3
import json

from pathlib import Path
from datetime import datetime, timezone


BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

DATABASE_FILE = DATA_DIR / "sensor_data.db"

JSON_FILE = DATA_DIR / "sensor_log.json"


def get_connection():

    connection = sqlite3.connect(DATABASE_FILE)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS sensor_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            device_id TEXT NOT NULL,

            distance_cm REAL NOT NULL,

            water_level_cm REAL NOT NULL,

            rainfall_mm REAL NOT NULL,

            received_at TEXT NOT NULL
        )
    """)

    connection.commit()

    connection.close()


def save_sensor_data(sensor_data):

    received_at = datetime.now(timezone.utc).isoformat()

    # Add timestamp to the data
    sensor_data_with_time = {
        **sensor_data,
        "received_at": received_at
    }

    # -----------------------------
    # SAVE TO SQLITE DATABASE
    # -----------------------------

    connection = get_connection()

    connection.execute("""
        INSERT INTO sensor_logs (
            device_id,
            distance_cm,
            water_level_cm,
            rainfall_mm,
            received_at
        )

        VALUES (?, ?, ?, ?, ?)
    """, (
        sensor_data["device_id"],
        sensor_data["distance_cm"],
        sensor_data["water_level_cm"],
        sensor_data["rainfall_mm"],
        received_at
    ))

    connection.commit()

    connection.close()


    # -----------------------------
    # SAVE TO JSON LOG
    # -----------------------------

    if JSON_FILE.exists():

        with open(JSON_FILE, "r", encoding="utf-8") as file:

            try:
                logs = json.load(file)

            except json.JSONDecodeError:
                logs = []

    else:

        logs = []


    logs.append(sensor_data_with_time)


    with open(JSON_FILE, "w", encoding="utf-8") as file:

        json.dump(
            logs,
            file,
            indent=4
        )


    return received_at


def get_sensor_logs(limit=100):

    connection = get_connection()

    rows = connection.execute("""
        SELECT
            id,
            device_id,
            distance_cm,
            water_level_cm,
            rainfall_mm,
            received_at

        FROM sensor_logs

        ORDER BY id DESC

        LIMIT ?
    """, (limit,)).fetchall()

    connection.close()

    return [dict(row) for row in rows]