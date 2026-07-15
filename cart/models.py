from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q



class Cart(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return f"{self.user.username}'s cart"
  
  @property
  def total_price(self):
    return sum(item.subtotal for item in self.items.all(), start=0)
  
  
  
class CartItem(models.Model):
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
  product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True)
  shop_product = models.ForeignKey('products.Shop_product', on_delete=models.CASCADE, null=True, blank=True)
  quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
  price = models.DecimalField(max_digits=10, decimal_places=2)
  added_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    constraints = [
      models.CheckConstraints(
        condition=(
          Q(product__isnull=False, shop_product__isnull=True)
          | Q(product__isnull=True, shop_product__isnull=False)
        ),
        name='cartitem_product_xor_shop_product',
      ),
      models.CheckConstraints(
        condition=Q(quantity__gte=1),
        name='cartitem_item_quantity_min_1',
      ),
      models.UniqueConstraints(fields=['cart', 'product'], name='unique_product_per_cart'),
      models.UniqueConstraints(fields=['cart', 'shop_product'], name='unique_shop_product_per_cart'),
    ]

  def clean(self):
    if self.product and self.shop_product:
      raise ValidationError('A cart item cannot have both a product and a shop product')
    if not self.product and not self.shop_product:
      raise ValidationError('A cart item must have either a product or a shop product')
      
  def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)
      
  def __str__(self):
    name = self.product.name if self.product else self.shop_product.name
    return f"{self.quantity} x {name}"
    
  @property
  def subtotal(self):
    return self.price * self.quantity

