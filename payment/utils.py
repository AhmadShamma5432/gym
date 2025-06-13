import json
import base64
import requests
import base64
import json
import os 
from dotenv import load_dotenv
import hashlib
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import random

# ==================== UTILITY FUNCTIONS ==================== #
import os
print("Current working directory:", os.getcwd())
# Load environment variables from .env
load_dotenv()

def generate_random_number():
    return random.randint(10000000, 999999999) 

def generate_signature(data_dict):
    """
    Takes a dictionary, converts to compact JSON,
    signs using RSA private key, returns Base64 signature
    """
    private_key_pem = os.getenv("PRIVATE_KEY")
    if private_key_pem == None:
        raise ValueError("where is private_key???")
    private_key = RSA.import_key(private_key_pem)
    h = SHA256.new(data_dict.encode())
    signature = pkcs1_15.new(private_key).sign(h)
    encoded_signature = base64.b64encode(signature).decode()

    return encoded_signature

def hash_otp_to_base64(otp: str) -> str:
    otp_bytes = otp.strip().encode('utf-8')
    hash_bytes = hashlib.sha256(otp_bytes).digest()
    return base64.b64encode(hash_bytes).decode('utf-8')


MTN_CREATE_INVOICE_URL = os.getenv("MTN_CREATE_INVOICE_URL")
TERMINAL_ID = os.getenv("TERMINAL_ID")
def create_invoice(amount, invoice_id, ttl=300):
    try:
        payload = {"Amount":amount*100,"Invoice":invoice_id,"TTL":ttl}
        payload_formatted = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        
        signature = generate_signature(str(payload_formatted))

        headers = {
            "Subject": TERMINAL_ID,
            "Request-Name": "pos_web/invoice/create",
            "X-Signature": signature,
            "Accept-Language": "en"
        }

        response = requests.post(
            MTN_CREATE_INVOICE_URL,
            json=payload,
            headers=headers,
            verify=True
        )

        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"raw_response": response.text}

        return {
            "status_code": response.status_code,
            "request": payload,
            "response": response_data
        }

    except Exception as e:
        return {"error": str(e)}
    
MTN_PAYMENT_INITIATE = os.getenv("MTN_PAYMENT_INITIATE")

def initiate_payment(phone, invoice_id,guid):
    try:
        payload = {"Phone":phone,"Invoice":invoice_id,"Guid":guid}
        # Format the payload as compact JSON string for signature generation
        payload_formatted = json.dumps(payload, separators=(',', ':'))
        payload_str = str(payload_formatted)
        signature = generate_signature(payload_str)

        headers = {
            "Subject": TERMINAL_ID,
            "X-Signature": signature,
            "Request-Name": "pos_web/payment_phone/initiate",
            "Accept-Language": "en"
        }
        response = requests.post(
            url=MTN_PAYMENT_INITIATE,
            json=payload,
            headers=headers,
            verify=True
        )
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {"raw_response": response.text}

        return {
            "status_code": response.status_code,
            "request": payload,
            "response": response_data
        }

    except Exception as e:
        return {
            "error": str(e)
        }