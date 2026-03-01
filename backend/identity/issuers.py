"""
Issuer Registry – defines all trusted issuers and their key paths.
Each issuer has its own RSA key pair for independent signing/verification.
"""

import os

KEY_DIR = os.path.dirname(os.path.abspath(__file__))

# ──────────────────────────────────────────────────────────────────────────────
# Issuer Registry
# ──────────────────────────────────────────────────────────────────────────────
ISSUER_REGISTRY = {
    "did:veracity:mlritm": {
        "name": "MLR Institute of Technology and Management",
        "short": "MLRITM",
        "color": "#4f8ef7",
        "private_key": os.path.join(KEY_DIR, "mlritm_private.pem"),
        "public_key":  os.path.join(KEY_DIR, "mlritm_public.pem"),
    },
    "did:veracity:external": {
        "name": "External Certification Authority",
        "short": "External CA",
        "color": "#34d399",
        "private_key": os.path.join(KEY_DIR, "external_private.pem"),
        "public_key":  os.path.join(KEY_DIR, "external_public.pem"),
    },
    "did:veracity:govt": {
        "name": "Government Digital Registry",
        "short": "Govt Registry",
        "color": "#f59e0b",
        "private_key": os.path.join(KEY_DIR, "govt_private.pem"),
        "public_key":  os.path.join(KEY_DIR, "govt_public.pem"),
    },
}

# Legacy fallback: existing keys mapped to the primary issuer
_LEGACY_PRIVATE = os.path.join(KEY_DIR, "private_key.pem")
_LEGACY_PUBLIC  = os.path.join(KEY_DIR, "public_key.pem")

if os.path.exists(_LEGACY_PRIVATE):
    ISSUER_REGISTRY["did:veracity:mlritm"]["private_key_legacy"] = _LEGACY_PRIVATE
    ISSUER_REGISTRY["did:veracity:mlritm"]["public_key_legacy"]  = _LEGACY_PUBLIC


def get_issuer(did: str) -> dict:
    """Return issuer info dict or raise KeyError."""
    if did not in ISSUER_REGISTRY:
        raise KeyError(f"Unknown issuer: {did}")
    return ISSUER_REGISTRY[did]


def list_issuers() -> list:
    """Return [{did, name, short}] for all registered issuers."""
    return [
        {"did": did, "name": info["name"], "short": info["short"]}
        for did, info in ISSUER_REGISTRY.items()
    ]
