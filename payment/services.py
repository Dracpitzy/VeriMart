import hashlib
import hmac
from decimal import Decimal
from django.conf import settings
import requests

PAYSTACK_BASE_URL = 'https://api.paystack.co'

PLATFORM_COMMISSION_RATE = Decimal('0.07')
LOCAL_CARD_PERCENTAGE = Decimal('0.015')
LOCAL_CARD_FLAT_FEE = Decimal('100')
LOCAL_CARD_FEE_CAP = Decimal('2000')
FEE_WAIVED_THRESHOLD = Decimal('2500')

def calculate_amount_with_fee(order_amount):
  if order_amount <= FEE_WAIVED_THRESHOLD:
    return order_amount
  
  amount_with_fee = (order_amount + LOCAL_CARD_FLAT_FEE) / (1 - LOCAL_CARD_PERCENTAGE)
  fee_charged = amount_with_fee - order_amount
  
  if fee_charged > LOCAL_CARD_FEE_CAP:
    amount_with_fee = order_amount + LOCAL_CARD_FEE_CAP
    return amount_with_fee.quantize(Decimal('0.01'))



def initialize_transaction(payment, email): 
  url = f'{PAYSTACK_BASE_URL}/transaction/initialize'
  headers = {
    'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
    'Content-type': 'application/json',
  }
  
  charge_amount = calculate_amount_with_fee(payment.amount)
  
  payload = {
    'email': email,
    'amount': int(charge_amount * 100),
    'reference': payment.transaction_reference,
  }
  
  response = requests.post(url, json=payload, headers=headers, timeout=10)
  response.raise_for_status()
  data = response.json()
  
  return data['data']['authorization_url']
  
  
def verify_transaction(reference):
  url = f'{PAYSTACK_BASE_URL}/transaction/verify/{reference}'
  
  headers = {
    'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
  }
  
  response = requests.get(url, headers=headers, timeout=10)
  response.raise_for_status
  data = response.json()
  
  transaction_data = data.get('data', {})
  return {
    'success': transaction_data.get('status') == 'success',
    'amount': transaction_data.get('amount'),
    'currency': transaction_data.get('currency'),
    'paid_at': transaction_data.get('paid_at'),
    'raw': transaction_data,
  }
  

def verify_webhook_signature(request):
  signature = request.headers.get('x-paystack-signature')
  if not signature:
    return False
    
  computed_signature = hmac.new(
    key=settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
    msg=request.body,
    digestmod=hashlib.sha512,
  ).hexdigest()
  
  return hmac.compare_digest(computed_signature, signature)
