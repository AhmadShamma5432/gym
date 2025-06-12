from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import base64
import hashlib

# Public Key (The same key that has been shared with me)
public_req = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDhiGpsGVdFb96F/nowO3jXWunNCJtyjZRVh/UO4j6tJBrAjguZq2pWPfxwhfufbsh1G3BSMFazNv9OwKQLrcCemO1DnwbL84aorNYqAn/8kcW41cq0jk2EdmC9v07N1cxaYpZF0cw7P0eK3Km2e9cU3bit+5UeCrUKvTbGy32LZwIDAQAB"

# Private Key (The same key that has been shared with me)
private_req = """-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQDhiGpsGVdFb96F/nowO3jXWunNCJtyjZRVh/UO4j6tJBrAjguZ
q2pWPfxwhfufbsh1G3BSMFazNv9OwKQLrcCemO1DnwbL84aorNYqAn/8kcW41cq0
jk2EdmC9v07N1cxaYpZF0cw7P0eK3Km2e9cU3bit+5UeCrUKvTbGy32LZwIDAQAB
AoGAY59Tix6Ce0yYGc44ARg0H8Sr5AK6T5aUgFeG+yUbFHYPTyEvpJigZyoIWVgF
tv5Dk98j9Voe4hkYG5ximjoNC+zoC6cKJlTRM9fGdEQqS+YTUkxQEhNDCvl5me2E
xEP8/OQQIx/AexrefdWqC00vZ2vci7EoZXc/ccBoThEi7IECQQD88ovA/uI0qquP
+mKpMe3AWPBSIVo6i5phv5FciwTJ3H7ThizbG2NLH8JXPGp1lJjtFqZfTEMxG+es
YUTu1mXBAkEA5EEs583oW4LDtAnFgQX30pccr8AKeH/qe5gPtx0DttQOTyT5eWVX
lWnhKCRJz8eculzl5OvdIDYhE84H1yTLJwJBAN1CkOsGSfrF3AK6g/j6er0JT1aY
ZCPYH/gnKVEpLcwhuzLuKGiVAXsiUc4bRAiMLmUdrfSochIQFcxc3X6KPkECQQCy
B1OrCSLuHTPfPK/bTnhYvJwXSEXiboLJG3VGcU7wTr1KZaBfWvfRBeAjmwonEZ3g
jYyR3JWABjgOZmgfGgeJAkEAkxgpuDZZrNcAjeGC2cbRaJScC4cgGJpydWVwh8qT
6q2+3BK59v8q4224ZwNsv+8aH0kE3JZnBLFxUUoxtC8x3g==
-----END RSA PRIVATE KEY-----"""

# private key
private_key = RSA.import_key(private_req)

# Request data
# request = '{"Secret":"85749837","Key":"MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDhiGpsGVdFb96F/nowO3jXWunNCJtyjZRVh/UO4j6tJBrAjguZq2pWPfxwhfufbsh1G3BSMFazNv9OwKQLrcCemO1DnwbL84aorNYqAn/8kcW41cq0jk2EdmC9v07N1cxaYpZF0cw7P0eK3Km2e9cU3bit+5UeCrUKvTbGy32LZwIDAQAB","Serial":"Test_Python"}'
# request = '{"Amount":1,"Invoice":2025051802,"TTL":15}'
request = '{"Phone":"963948526286","Invoice":1,"Guid":"200024"}'
# request = '{"Phone":"963947222548","Guid":"2025051802","OperationNumber":7287541413925984,"Invoice":2025051802,"Code":"BbR8dqXa3b6JqhX7HLHTgqorQk2fHRA7cNT3TtvXeOk="}'

# Sign
h = SHA256.new(request.encode())
signature = pkcs1_15.new(private_key).sign(h)
encoded_signature = base64.b64encode(signature).decode()

print('Signature (Base64): ' + encoded_signature)



# OTP hashing
OTP = '914389'
hashed = hashlib.sha256(OTP.encode()).digest()
base64_encoded = base64.b64encode(hashed).decode()

print("encode OTP: " + base64_encoded)