from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json
import os

MASTER_KEY = b'mpsf-master-key'

# Sinh khóa AES ngẫu nhiên 256-bit (32 bytes)
def generate_aes_key():
    return get_random_bytes(32)  # 256-bit

# Mã hóa file sử dụng AES-GCM
def encrypt_file(input_file_path, output_file_path, key):
    cipher = AES.new(key, AES.MODE_GCM)
    nonce = cipher.nonce

    with open(input_file_path, 'rb') as f:
        plaintext = f.read()

    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    with open(output_file_path, 'wb') as f:
        f.write(nonce + tag + ciphertext)

    return {
        'nonce': base64.b64encode(nonce).decode(),
        'tag': base64.b64encode(tag).decode()
    }

# Giải mã file AES-GCM
def decrypt_file(encrypted_file_path, output_file_path, key):
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

    print(f"[DEBUG] Giải mã: {encrypted_file_path}")
    print(f"[DEBUG] Ghi ra: {output_file_path}")
    print(f"[DEBUG] Key dài: {len(key)}")

    try:
        with open(encrypted_file_path, 'rb') as f:
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()

        print(f"[DEBUG] Nonce: {nonce.hex()}")
        print(f"[DEBUG] Tag: {tag.hex()}")
        print(f"[DEBUG] Ciphertext: {len(ciphertext)} bytes")
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)

        with open(output_file_path, 'wb') as f:
            f.write(plaintext)

        print(f"[✅] File đã được giải mã thành công: {output_file_path}")

    except Exception as e:
        print(f"[❌] Decryption failed: {e}")
        raise

# Mã hóa nội dung file và trả về dữ liệu mã hóa (dùng cho stream)
def encrypt_bytes(data, key):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return cipher.nonce + tag + ciphertext

# Giải mã nội dung mã hóa (dùng cho stream)
def decrypt_bytes(data, key):
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)
