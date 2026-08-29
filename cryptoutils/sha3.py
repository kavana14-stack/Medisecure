import hashlib

def hash_data(data):
    """Generates a SHA-3-256 hexadecimal digest for given string/bytes."""
    if not isinstance(data, str):
        data = str(data)
    return hashlib.sha3_256(data.encode("utf-8")).hexdigest()

def verify_hash(data, stored_hash):
    """Verifies if data matches the stored SHA-3-256 hash."""
    return hash_data(data) == stored_hash

def build_hash_chain(records):
    """Builds/rebuilds the hash chain in strict chronological order."""
    previous_hash = "0" * 64
    for record in records:
        record.prev_hash = previous_hash
        record_data = (
            f"{record.id}|"
            f"{record.diagnosis_nonce}|"
            f"{record.encrypted_diagnosis}|"
            f"{record.clinical_notes}"
        )
        record.record_hash = hash_data(previous_hash + record_data)
        record.save(update_fields=["prev_hash", "record_hash"])
        previous_hash = record.record_hash