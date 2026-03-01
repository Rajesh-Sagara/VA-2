import hashlib
import json
import os
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHAIN_PATH = os.path.join(BASE_DIR, "chain.json")


def load_chain():
    if not os.path.exists(CHAIN_PATH):
        return []

    with open(CHAIN_PATH, "r") as f:
        return json.load(f)


def save_chain(chain):
    with open(CHAIN_PATH, "w") as f:
        json.dump(chain, f, indent=4)


def calculate_block_hash(block):
    block_copy = block.copy()
    block_copy.pop("block_hash", None)
    block_string = json.dumps(block_copy, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()


def create_genesis_block():
    return {
        "index": 0,
        "timestamp": time.time(),
        "data": "Genesis Block",
        "previous_hash": "0",
        "block_hash": "0"
    }


def anchor_hash(file_hash: str, issuer_did: str):
    chain = load_chain()

    if not chain:
        genesis = create_genesis_block()
        genesis["block_hash"] = calculate_block_hash(genesis)
        chain.append(genesis)

    last_block = chain[-1]

    block = {
        "index": len(chain),
        "timestamp": time.time(),
        "file_hash": file_hash,
        "issuer_did": issuer_did,
        "previous_hash": last_block["block_hash"]
    }

    block["block_hash"] = calculate_block_hash(block)

    chain.append(block)
    save_chain(chain)

    return block


def verify_chain():
    chain = load_chain()
    if len(chain) <= 1:
        return True

    for i in range(1, len(chain)):
        current = chain[i]
        previous = chain[i - 1]

        if current["previous_hash"] != previous["block_hash"]:
            return False

        if calculate_block_hash(current) != current["block_hash"]:
            return False

    return True
