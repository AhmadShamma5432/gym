import hashlib
import base64

def hash_otp(otp: str) -> str:
    otp_bytes = otp.strip().encode('utf-8')
    hash_bytes = hashlib.sha256(otp_bytes).digest()
    return base64.b64encode(hash_bytes).decode('utf-8')

# Test it
print(hash_otp("123456"))