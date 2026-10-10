from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from products.models import Shop, Shop_product


class Event(models.Model):
  
  shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='events')
  name = models.CharField(max_length=200)
  start_date = models.DateTimeField()
  end_date = models.DateTimeField()
  percent_off = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(100)])
  flyer = models.ImageField(upload_to='event_flyers/', null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    ordering = ['-start_date']
    constraints = [
      models.CheckConstraint(condition=models.Q(end_date__gt=models.F('start_date')), name='event_end_after_start'),
    ]
    
  def __str__(self):
    return f"{self.name} ({self.shop.name})"
    
    
    
class EventItem(models.Model):
  
  event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='items')
  shop_product = models.ForeignKey(Shop_product, on_delete=models.CASCADE, related_name='event_items')
  percent_off = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(100)])
  created_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    constraints = [
      models.UniqueConstraint(fields=['event', 'shop_product'], name='unique_product_per_event'),
    ]
    
  def __str__(self):
    return f"{self.shop_product.name} in {self.event.name}"
