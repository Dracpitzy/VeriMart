import requests
from django.conf import settings
from django.template.loader import render_to_string
from collections import defaultdict
from decimal import Decimal

def send_email(to: str, subject: str, html: str):
  payload = {
    "from": settings.DEFAULT_FROM_EMAIL,
    "to": [to],
    "subject": subject,
    "html": html,
  }
  headers = {
    "Authorization": f"Bearer {settings.EMAIL_API_KEY}",
    "Content-Type": "application/json",
  }
  
  try:
    response = requests.post(
      settings.EMAIL_API_URL, json=payload, headers=headers, timeout=10
    )
    response.raise_for_status()
    return True
  except requests.RequestException:
    return False
    
    
def _display_name(user):
  return user.username
  
  
def send_order_confirmation_email(order):
  order_items = []
  
  for item in order.items.all():
    if item.product:
      name = item.product.name
      seller_name = _display_name(item.product.user)
    else:
      name = item.shop_product.name
      seller_name = item.shop_product.shop.name
    
    order_items.append({
      "name": name,
      "seller_name": seller_name,
      "quantity": item.quantity,
      "subtotal": f"{item.subtotal:,.2f}",
    })
  
  context = {
    "customer_name": _display_name(order.user),
    "order": order,
    "order_items": order_items,
    "total_paid": f"{order.total_price:,.2f}",
    "order_url": "#",
  }
  
  html = render_to_string("payment/email/order_confirmation.html", context)
  
  return send_email(
    to=order.user.email,
    subject=f"Order #{order.id} confirmed - VeriMart",
    html=html
  )
  
  
def send_seller_sale_notifications(order):
  
  seller_items = defaultdict(list)
  for item in order.items.all():
    seller = item.product.user if item.product else item.shop_product.shop.owner
    seller_items[seller].append(item)
    
  results = {}
  for seller, items in seller_items.items():
    if not seller.email:
      results[seller.id] = False
      continue
    
    gross_amoumt = sum(item.subtotal for item in items)
    commision_amount = gross_amoumt * Decimal("0.07")
    net_earnings = gross_amoumt - commision_amount
    
    items_context = [
      {
        "name": item.product.name if item.product else item.shop_product.name,
        "quantity": item.quantity,
        "price": f"{item.subtotal:,.2f}",
      }
      for item in items
    ]
    
    context = {
      "seller_name": _display_name(seller),
      "order": order,
      "items": items_context,
      "buyer_name": _display_name(order.user),
      "gross_amoumt": f"{gross_amoumt:,.2f}",
      "commision_amount": f"{commision_amount:,.2f}",
      "net_earnings": f"{net_earnings:,.2f}",
      "order_url": "#"
    }
    
    html = render_to_string("payment/emails/seller_sale_notification.html", context)
    
    results[seller.id] = send_email(
      to=seller.email,
      subject=f"New sale on Order #{order.id} - VeriMart",
      html=html,
    )
    
  return results