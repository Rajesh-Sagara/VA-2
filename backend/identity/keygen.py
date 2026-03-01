"""
Key Generator – generates RSA-2048 key pairs for all issuers that don't yet
have key files on disk. Safe to re-run; existing keys are never overwritten.

Usage:
    python -m backend.identity.keygen
"""

import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

KEY_DIR = os.path.dirname(os.path.abspath(__file__))

ISSUERS_KEYS = {
    "mlritm":   ("mlritm_private.pem",   "mlritm_public.pem"),
    "external": ("external_private.pem", "external_public.pem"),
    "govt":     ("govt_private.pem",     "govt_public.pem"),
}


def generate_key_pair(private_path: str, public_path: str):
    """Generate and save an RSA-2048 key pair if not already present."""
    if os.path.exists(private_path) and os.path.exists(public_path):
        print(f"  [SKIP] Keys already exist: {os.path.basename(private_path)}")
        return

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Save private key
    with open(private_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # Save public key
    with open(public_path, "wb") as f:
        f.write(private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ))

    print(f"  [OK]   Generated: {os.path.basename(private_path)} / {os.path.basename(public_path)}")


def ensure_legacy_symlink():
    """
    Ensure the legacy private_key.pem / public_key.pem also exist
    (pointing to the MLRITM keys) for backwards compatibility.
    """
    legacy_priv = os.path.join(KEY_DIR, "private_key.pem")
    legacy_pub  = os.path.join(KEY_DIR, "public_key.pem")
    mlritm_priv = os.path.join(KEY_DIR, "mlritm_private.pem")
    mlritm_pub  = os.path.join(KEY_DIR, "mlritm_public.pem")

    if not os.path.exists(legacy_priv) and os.path.exists(mlritm_priv):
        import shutil
        shutil.copy2(mlritm_priv, legacy_priv)
        shutil.copy2(mlritm_pub,  legacy_pub)
        print("  [OK]   Copied MLRITM keys → legacy private_key.pem / public_key.pem")


def run():
    print("=" * 50)
    print("Veracity Agent – Key Generator")
    print("=" * 50)
    for issuer_id, (priv_file, pub_file) in ISSUERS_KEYS.items():
        print(f"\nIssuer: {issuer_id}")
        generate_key_pair(
            os.path.join(KEY_DIR, priv_file),
            os.path.join(KEY_DIR, pub_file),
        )
    ensure_legacy_symlink()
    print("\n✓ Key generation complete.\n")


if __name__ == "__main__":
    run()
