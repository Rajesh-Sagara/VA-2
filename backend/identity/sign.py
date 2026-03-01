"""
Digital signing & verification – supports multiple issuers.
Each issuer has its own RSA key pair stored in the identity directory.
"""

import base64
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from backend.identity.issuers import get_issuer

KEY_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_private_key(issuer_did: str):
    info = get_issuer(issuer_did)
    key_path = info["private_key"]

    # Fallback to legacy path for the primary issuer
    if not os.path.exists(key_path):
        legacy = info.get("private_key_legacy", "")
        if os.path.exists(legacy):
            key_path = legacy
        else:
            raise FileNotFoundError(
                f"Private key not found for {issuer_did}: {key_path}\n"
                "Run: python -m backend.identity.keygen"
            )

    with open(key_path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def _load_public_key(issuer_did: str):
    info = get_issuer(issuer_did)
    key_path = info["public_key"]

    if not os.path.exists(key_path):
        legacy = info.get("public_key_legacy", "")
        if os.path.exists(legacy):
            key_path = legacy
        else:
            raise FileNotFoundError(
                f"Public key not found for {issuer_did}: {key_path}\n"
                "Run: python -m backend.identity.keygen"
            )

    with open(key_path, "rb") as f:
        return serialization.load_pem_public_key(f.read())


def sign_hash(file_hash: str, issuer_did: str) -> str:
    """Sign a file hash with the specified issuer's private key."""
    private_key = _load_private_key(issuer_did)
    signature = private_key.sign(
        file_hash.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return base64.b64encode(signature).decode()


def verify_signature(file_hash: str, signature: str, issuer_did: str) -> bool:
    """Verify a signature using the specified issuer's public key."""
    try:
        public_key = _load_public_key(issuer_did)
        public_key.verify(
            base64.b64decode(signature),
            file_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except Exception:
        return False
