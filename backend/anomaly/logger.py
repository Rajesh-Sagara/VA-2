import json
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(BASE_DIR, "events.json")


def log_event(event_type: str, details: dict):
    event = {
        "event_type": event_type,
        "timestamp": time.time(),
        "details": details
    }

    if not os.path.exists(LOG_PATH):
        with open(LOG_PATH, "w") as f:
            json.dump([], f)

    with open(LOG_PATH, "r+") as f:
        data = json.load(f)
        data.append(event)
        f.seek(0)
        json.dump(data, f, indent=4)
