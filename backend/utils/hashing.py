import hashlib

def generate_hash(data: bytes) -> str:
    """
    Generates SHA-256 hash for given data
    """
    sha = hashlib.sha256()
    sha.update(data)
    return sha.hexdigest()
