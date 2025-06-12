# views.py
import json
import requests
from store.models import Order
from django.views import View
from django.http import JsonResponse
from .utils import generate_signature,hash_otp_to_base64
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import os 
from dotenv import load_dotenv

load_dotenv() 

MTN_CONFIRM_PAYMENT_URL = os.getenv('MTN_CONFIRM_PAYMENT_URL')
TERMINAL_ID = os.getenv('TERMINAL_ID')

@method_decorator(csrf_exempt, name='dispatch')
class ConfirmPaymentView(View):

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            code = data.get("code")  
            order_id = data.get("order_id")
            try: 
                order = Order.objects.get(pk=order_id)
            except: 
                raise ValueError({"message":"the order you are trying to confirm is not exists"})
            
            if not all([order_id,code]):
                return JsonResponse({
                    "error": "Missing required fields: phone, guid, code, invoice"
                }, status=400)

            hashed_code = hash_otp_to_base64(code)
            payload = {"Code":str(hashed_code),"Guid":str(order.guid),"Invoice":order.invoice_id,"OperationNumber":order.operation_number,"Phone":str(order.phone)}

            payload_formatted = json.dumps(payload, separators=(',', ':'), sort_keys=True)
            payload_str = str(payload_formatted) 
            signature = generate_signature(payload_str)

            headers = {
                "Subject": TERMINAL_ID,
                "X-Signature": signature,
                "Request-Name": "pos_web/payment_phone/confirm",
                "Accept-Language": "en"
            }

            response = requests.post(
                url=MTN_CONFIRM_PAYMENT_URL,
                json=payload, 
                headers=headers,
                verify=True
            )

            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"raw_response": response.text}

            return JsonResponse({
                "status_code": response.status_code,
                "request": payload,
                "response": response_data
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON input"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)