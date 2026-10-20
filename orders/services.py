from django.db import transaction
from django.db.models import F
from products.models import Product, Shop_product
from .models import Order

from payment.services import release_pending_to_available
from products.services import update_verification_status


class InsufficientStock(Exception):
  def __init__(self, name):
    self.name = name
    super().__init__(name)
    
    
def reserve_order_stock(order):
  for item in order.items.all():
    if item.product_id:
      model, pk = Product, item.product_id
    elif item.shop_product_id:
      model, pk = Shop_product, item.shop_product_id
    else:
      continue
    
    updated = model.objects.filter(pk=pk, stock__gte=item.quantity).update(stock=F('stock') - item.quantity)
    
    if updated == 0:
      product = item.product or item.shop_product
      raise InsufficientStock(product.name)
      
    order.stock_reserved = True
    order.save(update_fields=['stock_reserved', 'updated_at'])


def release_order_stock(order):
  with transaction.atomic():
    locked_order = Order.objects.select_for_update().get(pk=order.pk)
    
    if not locked_order.stock_reserved:
      return False
      
    for item in locked_order.items.all():
      
      if item.product_id:
        Product.objects.filter(pk=item.product_id).update(stock=F('stock') + item.quantity)
      elif item.shop_product_id:
        Shop_product.objects.filter(pk=item.shop_product_id).update(stock=F('stock') + item.quantity)
      
    locked_order.stock_reserved = False
    locked_order.save(update_fields=['stock_reserved', 'updated_at'])
    
  order.stock_reserved = False
  return True
  
  
DELIVERABLE_STATUSES = ('paid', 'processing', 'shipped')

def mark_order_delivered(order):
  
  with transaction.atomic():
    locked_order = Order.objects.select_for_update().get(pk=order.pk)
    if locked_order.status not in DELIVERABLE_STATUSES:
      return False
    
    locked_order.status = 'delivered'
    locked_order.save(update_fields=['status', 'updated_at'])
    release_pending_to_available(locked_order)
    
    shops = {item.shop_product.shop for item in locked_order.items.select_related('shop_product__shop') if item.shop_product}
    for shop in shops:
      update_verification_status(shop)
      
  order.status = 'delivered'
  return True
  
  
def cancel_unpaid_order(order):
  with transaction.atomic():
    locked_order = Order.objects.select_for_update().get(pk=order.pk)
    if locked_order.status != 'pending':
      return False
      
    locked_order.status = 'cancelled'
    locked_order.save(update_fields=['status', 'updated_at'])
    release_order_stock(locked_order)
    
    order.status = 'cancelled'
    order.stock_reserved = False
    return True
    
  
def get_order_problems(order):
  problems = []
  
  for item in order.items.select_related('product', 'shop_product__shop'):
    
    if item.product is None and item.shop_product is None:
      problems.append('An item in this order is no longer available')
      continue
    
    target = item.product or item.shop_product
    
    if item.product and item.product.is_deleted:
      problems.append(f'{target.name} is no longer available')
    elif item.shop_product and not item.shop_product.is_available:
      problems.append(f'{target.name} is no longer available')
    elif item.shop_product and not item.shop_product.shop.is_active:
      problems.append(f'{target.name} is from a shop that is currently inactive')
      
  return problems