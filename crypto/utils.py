# crypto/utils.py
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

MASTER_KEY = b"mpsf-master-key-32byteslong!@#"  # 32 byte = 256-bit

def encrypt_key_with_master(aes_key: bytes) -> str:
    cipher = AES.new(MASTER_KEY, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(aes_key)
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

def decrypt_key_with_master(encrypted_str: str) -> bytes:
    data = base64.b64decode(encrypted_str)
    nonce, tag, ciphertext = data[:16], data[16:32], data[32:]
    cipher = AES.new(MASTER_KEY, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
