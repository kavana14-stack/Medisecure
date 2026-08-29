import base64
import hashlib

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


def generate_keypair():
    """
    Generate an Ed25519 private/public key pair.
    """

    private_key = Ed25519PrivateKey.generate()

    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption()
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

    return (
        base64.b64encode(private_bytes).decode(),
        base64.b64encode(public_bytes).decode()
    )


def sign_data(data, private_key_b64):
    """
    Sign data using the doctor's Ed25519 private key.
    """

    private_bytes = base64.b64decode(private_key_b64)

    private_key = Ed25519PrivateKey.from_private_bytes(
        private_bytes
    )

    # Convert prescription data into a SHA3-256 hash
    data_hash = hashlib.sha3_256(
        data.encode()
    ).digest()

    signature = private_key.sign(data_hash)

    return base64.b64encode(signature).decode()


def verify_signature(
    data,
    signature_b64,
    public_key_b64
):
    """
    Verify that the signature belongs to
    the supplied data and public key.
    """

    try:

        public_bytes = base64.b64decode(
            public_key_b64
        )

        public_key = Ed25519PublicKey.from_public_bytes(
            public_bytes
        )

        signature = base64.b64decode(
            signature_b64
        )

        data_hash = hashlib.sha3_256(
            data.encode()
        ).digest()

        public_key.verify(
            signature,
            data_hash
        )

        return True

    except Exception:

        return False
