import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from django.conf import settings


def get_encryption_key():

    key = base64.urlsafe_b64decode(
        settings.MEDICAL_ENCRYPTION_KEY
    )

    if len(key) != 32:
        raise ValueError(
            "Medical encryption key must be exactly 32 bytes."
        )

    return key


def encrypt_data(plaintext):

    key = get_encryption_key()

    aesgcm = AESGCM(key)

    # Fresh 12-byte nonce for every encryption
    nonce = os.urandom(12)

    ciphertext = aesgcm.encrypt(
        nonce,
        plaintext.encode("utf-8"),
        None
    )

    return (
        base64.b64encode(nonce).decode("utf-8"),
        base64.b64encode(ciphertext).decode("utf-8")
    )


def decrypt_data(nonce, ciphertext):

    key = get_encryption_key()

    aesgcm = AESGCM(key)

    nonce_bytes = base64.b64decode(nonce)

    ciphertext_bytes = base64.b64decode(ciphertext)

    plaintext = aesgcm.decrypt(
        nonce_bytes,
        ciphertext_bytes,
        None
    )

    return plaintext.decode("utf-8")