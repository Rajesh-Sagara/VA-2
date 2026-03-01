from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from backend.utils.hashing import generate_hash
from backend.identity.sign import sign_hash, verify_signature
from backend.identity.issuers import list_issuers, get_issuer, ISSUER_REGISTRY
from backend.identity.keygen import run as generate_all_keys
from backend.blockchain.blockchain import anchor_hash, verify_chain, load_chain
from backend.anomaly.logger import log_event
from backend.anomaly.detector import detect_anomaly
from backend.response.responder import autonomous_response
from backend.utils.file_validator import validate_file
from backend.utils.excel_parser import parse_excel

import json
import time
import os

# ──────────────────────────────────────────────────────────────────────────────
# App Initialization
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Veracity Agent – Autonomous AI Trust System",
    description="Multi-issuer document integrity, authenticity & blockchain provenance system",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
STORAGE_DIR = os.path.join(BASE_DIR, "storage")
LEDGER_PATH = os.path.join(STORAGE_DIR, "local_ledger.json")

# ──────────────────────────────────────────────────────────────────────────────
# Startup: ensure all issuer keys exist
# ──────────────────────────────────────────────────────────────────────────────
@app.on_event("startup")
def startup_event():
    generate_all_keys()

# ──────────────────────────────────────────────────────────────────────────────
# Ledger Helpers
# ──────────────────────────────────────────────────────────────────────────────
def load_ledger():
    if not os.path.exists(LEDGER_PATH):
        return {"records": []}
    try:
        with open(LEDGER_PATH, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"records": []}


def save_ledger(data):
    os.makedirs(STORAGE_DIR, exist_ok=True)
    with open(LEDGER_PATH, "w") as f:
        json.dump(data, f, indent=4)


def hash_exists(ledger, file_hash: str) -> bool:
    return any(r["hash"] == file_hash for r in ledger.get("records", []))


def _build_record(filename, file_hash, signature, issuer_did, file_info: dict) -> dict:
    return {
        "filename":       filename,
        "hash":           file_hash,
        "signature":      signature,
        "issuer_did":     issuer_did,
        "issuer_name":    ISSUER_REGISTRY[issuer_did]["name"],
        "signature_algo": "RSA-PSS-SHA256",
        "issued_at":      time.time(),
        "revoked":        False,
        "file_type":      file_info.get("category", "other"),
        "mime_type":      file_info.get("mime_type", ""),
        "size_bytes":     file_info.get("size_bytes", 0),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Verify Helper (shared between single + batch)
# ──────────────────────────────────────────────────────────────────────────────
def _verify_content(content: bytes, filename: str, start_time: float) -> dict:
    incoming_hash = generate_hash(content)
    ledger = load_ledger()

    for record in ledger.get("records", []):
        if record["hash"] == incoming_hash:
            if record.get("revoked", False):
                return {
                    "filename":   filename,
                    "status":     "REVOKED",
                    "issuer":     record["issuer_did"],
                    "issuer_name": record.get("issuer_name", ""),
                    "latency_ms": round((time.time() - start_time) * 1000, 2),
                    "reason":     "Credential revoked by autonomous agent",
                }

            if record["issuer_did"] not in ISSUER_REGISTRY:
                return {
                    "filename":   filename,
                    "status":     "REJECTED",
                    "latency_ms": round((time.time() - start_time) * 1000, 2),
                    "reason":     "Untrusted issuer",
                }

            sig_valid = verify_signature(
                incoming_hash,
                record["signature"],
                record["issuer_did"]
            )

            log_event(event_type="verify", details={"count": 1, "hash": incoming_hash})
            latency_ms = round((time.time() - start_time) * 1000, 2)

            if sig_valid:
                return {
                    "filename":   filename,
                    "status":     "VERIFIED",
                    "issuer":     record["issuer_did"],
                    "issuer_name": record.get("issuer_name", ""),
                    "integrity":  "HASH MATCHED",
                    "authenticity": "SIGNATURE VALID",
                    "provenance": "BLOCKCHAIN ANCHORED",
                    "file_type":  record.get("file_type", ""),
                    "mime_type":  record.get("mime_type", ""),
                    "issued_at":  record.get("issued_at"),
                    "latency_ms": latency_ms,
                }
            else:
                return {
                    "filename":   filename,
                    "status":     "REJECTED",
                    "latency_ms": latency_ms,
                    "reason":     "Signature verification failed",
                }

    return {
        "filename":   filename,
        "status":     "TAMPERED OR UNKNOWN",
        "latency_ms": round((time.time() - start_time) * 1000, 2),
        "reason":     "Hash not found in ledger",
    }


# ==============================================================================
# 📋 ISSUER REGISTRY
# ==============================================================================
@app.get("/issuers")
def get_issuers():
    """Return all trusted issuers."""
    return {"issuers": list_issuers()}


# ==============================================================================
# 📥 SINGLE FILE REGISTER / SIGN / ANCHOR
# ==============================================================================
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    issuer_did: Optional[str] = Form(default="did:veracity:mlritm")
):
    start_time = time.time()

    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # Validate issuer
    if issuer_did not in ISSUER_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown issuer: {issuer_did}")

    content = await file.read()

    # File validation
    file_info = validate_file(content, file.filename)
    if not file_info["valid"]:
        raise HTTPException(status_code=422, detail=f"Invalid file: {file_info['message']}")

    file_hash = generate_hash(content)
    ledger = load_ledger()

    if hash_exists(ledger, file_hash):
        raise HTTPException(status_code=409, detail="Replay detected: File already registered")

    signature = sign_hash(file_hash, issuer_did)
    record = _build_record(file.filename, file_hash, signature, issuer_did, file_info)
    ledger["records"].append(record)
    save_ledger(ledger)

    block = anchor_hash(file_hash, issuer_did)
    log_event(event_type="upload", details={"count": 1, "hash": file_hash})

    latency_ms = round((time.time() - start_time) * 1000, 2)

    # Excel parsing info (returned but not stored in ledger)
    extra = {}
    if file_info["category"] == "spreadsheet":
        extra["spreadsheet_info"] = parse_excel(content, file.filename)

    return {
        "message":        "File registered, signed, and anchored",
        "hash":           file_hash,
        "issuer":         issuer_did,
        "issuer_name":    ISSUER_REGISTRY[issuer_did]["name"],
        "file_type":      file_info["category"],
        "mime_type":      file_info["mime_type"],
        "size_bytes":     file_info["size_bytes"],
        "block_index":    block["index"],
        "block_hash":     block["block_hash"],
        "upload_latency_ms": latency_ms,
        **extra,
    }


# ==============================================================================
# 📦 BATCH REGISTER (multiple files, one issuer)
# ==============================================================================
@app.post("/upload/batch")
async def upload_batch(
    files: List[UploadFile] = File(...),
    issuer_did: Optional[str] = Form(default="did:veracity:mlritm")
):
    if issuer_did not in ISSUER_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown issuer: {issuer_did}")

    ledger = load_ledger()
    results = []

    for f in files:
        start_time = time.time()
        try:
            content = await f.read()
            file_info = validate_file(content, f.filename)

            if not file_info["valid"]:
                results.append({
                    "filename": f.filename,
                    "status":   "FAILED",
                    "reason":   file_info["message"],
                    "latency_ms": 0,
                })
                continue

            file_hash = generate_hash(content)

            if hash_exists(ledger, file_hash):
                results.append({
                    "filename":  f.filename,
                    "status":    "DUPLICATE",
                    "reason":    "Already registered",
                    "hash":      file_hash,
                    "latency_ms": round((time.time() - start_time) * 1000, 2),
                })
                continue

            signature = sign_hash(file_hash, issuer_did)
            record = _build_record(f.filename, file_hash, signature, issuer_did, file_info)
            ledger["records"].append(record)

            block = anchor_hash(file_hash, issuer_did)
            log_event(event_type="upload", details={"count": 1, "hash": file_hash})

            results.append({
                "filename":   f.filename,
                "status":     "REGISTERED",
                "hash":       file_hash,
                "file_type":  file_info["category"],
                "mime_type":  file_info["mime_type"],
                "block_index": block["index"],
                "latency_ms": round((time.time() - start_time) * 1000, 2),
            })

        except Exception as e:
            results.append({
                "filename": f.filename,
                "status":   "ERROR",
                "reason":   str(e),
                "latency_ms": 0,
            })

    save_ledger(ledger)
    return {
        "issuer":       issuer_did,
        "issuer_name":  ISSUER_REGISTRY[issuer_did]["name"],
        "total_files":  len(files),
        "results":      results,
    }


# ==============================================================================
# 🔍 SINGLE FILE VERIFY
# ==============================================================================
@app.post("/verify")
async def verify_file(file: UploadFile = File(...)):
    start_time = time.time()
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    content = await file.read()
    return _verify_content(content, file.filename, start_time)


# ==============================================================================
# 🔍 BATCH VERIFY (multiple files)
# ==============================================================================
@app.post("/verify/batch")
async def verify_batch(files: List[UploadFile] = File(...)):
    results = []
    for f in files:
        start_time = time.time()
        content = await f.read()
        result = _verify_content(content, f.filename, start_time)
        results.append(result)
    return {
        "total_files": len(files),
        "results": results,
    }


# ==============================================================================
# 📊 EXCEL / SPREADSHEET PARSE (preview only, no registration)
# ==============================================================================
@app.post("/parse/spreadsheet")
async def parse_spreadsheet(file: UploadFile = File(...)):
    content = await file.read()
    result = parse_excel(content, file.filename)
    return result


# ==============================================================================
# 📘 LEDGER VIEWER
# ==============================================================================
@app.get("/ledger/view")
def view_ledger():
    return load_ledger()


# ==============================================================================
# 🗑️ LEDGER CLEAR
# ==============================================================================
@app.delete("/ledger/clear")
def clear_ledger():
    """Wipe all records from the off-chain ledger. Irreversible."""
    ledger = load_ledger()
    count = len(ledger.get("records", []))
    save_ledger({"records": []})
    log_event(event_type="clear_ledger", details={"removed_records": count})
    return {
        "message": "Ledger cleared",
        "records_removed": count,
    }


# ==============================================================================
# ⛓️ BLOCKCHAIN HEALTH CHECK
# ==============================================================================
@app.get("/blockchain/verify")
def blockchain_health_check():
    return {"blockchain_valid": verify_chain()}


# ==============================================================================
# ⛓️ BLOCKCHAIN BLOCK EXPLORER
# ==============================================================================
@app.get("/blockchain/blocks")
def view_blockchain_blocks():
    chain = load_chain()
    return {"total_blocks": len(chain), "chain": chain}


# ==============================================================================
# 🧠 AI ANOMALY DETECTION
# ==============================================================================
@app.get("/anomaly/check")
def anomaly_check():
    return detect_anomaly()


# ==============================================================================
# 🤖 AUTONOMOUS AGENT RESPONSE
# ==============================================================================
@app.post("/agent/respond")
def agent_autonomous_response():
    anomaly_result = detect_anomaly()
    response = autonomous_response(anomaly_result)
    return {
        "anomaly_result": anomaly_result,
        "agent_action":   response,
    }
