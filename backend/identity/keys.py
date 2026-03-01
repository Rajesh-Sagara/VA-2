from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os

KEY_DIR = os.path.dirname(os.path.abspath(__file__))


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    public_key = private_key.public_key()

    private_path = os.path.join(KEY_DIR, "private_key.pem")
    public_path = os.path.join(KEY_DIR, "public_key.pem")

    with open(private_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    with open(public_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    print("✅ Issuer keys generated successfully")
    print(f"🔐 Private key: {private_path}")
    print(f"🔓 Public key : {public_path}")


# 🔥 THIS IS THE IMPORTANT PART
if __name__ == "__main__":
    generate_keys()
