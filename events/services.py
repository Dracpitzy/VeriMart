from decimal import Decimal
from django.utils import timezone
from .models import EventItem


def get_active_event_item(shop_product):
  now = timezone.now()
  
  return (
    EventItem.objects.select_related('event').filter(
      shop_product=shop_product,
      event__start_date__lte=now,
      event__end_date__gte=now,
    ).order_by('-event__start_date').first()
  )
  

def get_current_price(shop_product):
  item = get_active_event_item(shop_product)
  if item is None:
    return shop_product.price
    
  percent_off = item.percent_off or item.event.percent_off
  if percent_off is None:
    return shop_product.price
    
  discount = shop_product.price * (Decimal(percent_off) / Decimal('100'))
  return (shop_product.price - discount).quantize(Decimal('0.01'))
    