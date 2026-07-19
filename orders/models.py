from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from products.models import Product, Shop_product


class Order(models.Model):
  STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('paid', 'Paid'),
    ('processing', 'Processing'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('cancelled', 'Cancelled')
  ]
    
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
  shipping_address = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return f"Order #{self.id} by {self.user}"
    
  @property
  def total_price(self):
    return sum(item.subtotal for item in self.items.all())
    
  
class OrderItem(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
  product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
  shop_product = models.ForeignKey(Shop_product, on_delete=models.SET_NULL, null=True, blank=True)
  quantity = models.PositiveIntegerField(default=1)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  
  def clean(self):
    if self.product and self.shop_product:
      raise ValidationError('An order item cannot have both a product and a shop product')
    if not self.product and not self.shop_product:
      raise ValidationError('An order item must have either a product or a shop product')
  
  def __str__(self):
    name = self.product.name if self.product else self.shop_product.name
    return f"{self.quantity} x {name}"
    
  @property
  def subtotal(self):
    return self.price * self.quantity
  
  
  


