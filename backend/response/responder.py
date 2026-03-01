import json
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEDGER_PATH = os.path.join(
    BASE_DIR, "..", "storage", "local_ledger.json"
)


def load_ledger():
    if not os.path.exists(LEDGER_PATH):
        return {"records": []}

    with open(LEDGER_PATH, "r") as f:
        return json.load(f)


def save_ledger(data):
    with open(LEDGER_PATH, "w") as f:
        json.dump(data, f, indent=4)


def autonomous_response(anomaly_result: dict):
    """
    Takes anomaly detection result and enforces actions automatically
    """
    if not anomaly_result.get("anomaly"):
        return {
            "action": "NONE",
            "message": "No anomaly detected"
        }

    ledger = load_ledger()
    actions = []

    for record in ledger.get("records", []):
        if not record.get("revoked", False):
            record["revoked"] = True
            record["revoked_at"] = time.time()
            actions.append(
                f"Credential revoked: {record['filename']}"
            )

    save_ledger(ledger)

    return {
        "action": "AUTO_REVOKE",
        "affected_records": actions,
        "message": "Anomaly detected, credentials revoked automatically"
    }
