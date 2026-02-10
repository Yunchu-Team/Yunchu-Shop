import base64
import hashlib
from cryptography.fernet import Fernet

def _derive_key(secret_key: str) -> bytes:
    digest = hashlib.sha256(secret_key.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest)

def _get_fernet(secret_key: str) -> Fernet:
    return Fernet(_derive_key(secret_key))

def encrypt_text(plain_text: str, secret_key: str) -> str:
    f = _get_fernet(secret_key)
    return f.encrypt(plain_text.encode('utf-8')).decode('utf-8')

def decrypt_text(cipher_text: str, secret_key: str) -> str:
    f = _get_fernet(secret_key)
    return f.decrypt(cipher_text.encode('utf-8')).decode('utf-8')
