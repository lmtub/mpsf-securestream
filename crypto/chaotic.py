import numpy as np

# Logistic Map
def logistic_map(seed=0.7, r=3.99, size=1024):
    x = seed
    result = []
    for _ in range(size):
        x = r * x * (1 - x)
        result.append(x)
    return result

# Tent Map
def tent_map(seed=0.7, size=1024):
    x = seed
    result = []
    for _ in range(size):
        if x < 0.5:
            x = 2 * x
        else:
            x = 2 * (1 - x)
        result.append(x)
    return result

# Chuyển đổi chuỗi chaotic thành byte stream để XOR
def chaotic_bytes(chaotic_sequence, scale=255):
    return bytes([int(x * scale) % 256 for x in chaotic_sequence])

# XOR hai byte stream (dùng cho mã hóa/giải mã stream)
def xor_stream(data: bytes, key_stream: bytes) -> bytes:
    return bytes([b ^ key_stream[i % len(key_stream)] for i, b in enumerate(data)])
