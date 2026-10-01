from django.db.models import Avg
from orders.models import OrderItem

VERIFICATION_MIN_COMPLETED_ORDERS = 20
VERIFICATION_MIN_REVIEWS = 10
VERIFICATION_MIN_RATING = 4.5

def update_verification_status(shop):
  
  completed_orders = OrderItem.objects.filter(shop_product__shop=shop, order__status='delivered').count()
  
  review_count = shop.reviews.count()
  average_rating = shop.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
  
  is_eligible = (
    completed_orders >= VERIFICATION_MIN_COMPLETED_ORDERS and review_count >= VERIFICATION_MIN_REVIEWS and average_rating >= VERIFICATION_MIN_RATING
  )
  
  if shop.is_verified != is_eligible:
    shop.is_verified = is_eligible
    shop.save(update_fields=['is_verified'])