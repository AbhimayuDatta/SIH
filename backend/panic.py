from datetime import datetime, timezone


def panic_check(ai_result):
    """
    Check the AI result and generate an emergency alert
    if the risk level is CRITICAL.
    """

    risk_level = ai_result.get("risk_level")

    if risk_level == "CRITICAL":

        alert = {
            "alert": True,
            "type": "PANIC",
            "device_id": ai_result.get("device_id"),
            "risk_level": "CRITICAL",
            "distance_cm": ai_result.get("distance_cm"),
            "message": "EMERGENCY FLOOD ALERT",
            "time": datetime.now(timezone.utc).isoformat()
        }

        return alert

    return {
        "alert": False,
        "type": "NONE",
        "message": "No emergency detected"
    }


# -------------------------------
# TEST
# -------------------------------

if __name__ == "__main__":

    # Pretend this came from the AI
    ai_result = {
        "device_id": "ESP001",
        "risk_level": "CRITICAL",
        "distance_cm": 42.5
    }

    result = panic_check(ai_result)

    print("===================================")
    print("       PANIC PIPELINE TEST")
    print("===================================")

    print(result)

