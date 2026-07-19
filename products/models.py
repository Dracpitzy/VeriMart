from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Category(models.Model):
  name = models.CharField(max_length=100, unique=True)
  
  def __str__(self):
    return self.name
    
  
class Shop(models.Model):
  owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shop')
  name = models.CharField(max_length=200, unique=True)
  description = models.TextField()
  logo = models.ImageField(upload_to='shops/logos/')
  is_active = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return self.name
    
    
class Shop_product(models.Model):
  shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop_products')
  category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='shop_products')
  name = models.CharField(max_length=200)
  description = models.TextField()
  stock = models.PositiveIntegerField(default=0)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  image = models.ImageField(upload_to='shop_products/')
  is_available = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return f"{self.name} - {self.shop.name} "
  

class Product(models.Model):
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product')
  category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
  name = models.CharField(max_length=100)
  description = models.TextField()
  price = models.DecimalField(max_digits=10, decimal_places=2)
  stock = models.PositiveIntegerField(default=0)
  image = models.ImageField(upload_to='products/')
  is_deleted = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  def __str__(self):
    return self.name
    
    
class ShopReview(models.Model):
  shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='reviews')
  buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
  comment = models.TextField(blank=True)
  is_deleted = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    unique_together = ('shop', 'buyer')
    constraints = [models.CheckConstraint(condition=models.Q(rating__gte=1) & models.Q(rating__lte=5), name='rating_between_1_and_5')]
    
  def __str__(self):
    return f"{self.buyer} rated {self.shop} - {self.rating}"
  

class ProductReview(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
  shop_product = models.ForeignKey(Shop_product, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
  buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
  rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
  comment = models.TextField(blank=True)
  is_deleted = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  
  class Meta:
    constraints = [
      models.CheckConstraint(
        condition=models.Q(rating__gte=1) & models.Q(rating__lte=5), name='product_rating_between_1_and_5'
      )
    ]
    
  def __str__(self):
    return f"{self.buyer} reviewed {self.product or self.shop_product} - {self.rating}"