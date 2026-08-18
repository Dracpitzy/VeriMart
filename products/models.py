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
    
    
class ShopBankDetail(models.Model):
  shop = models.OneToOneField(Shop, on_delete=models.CASCADE, related_name='bank_detail')
  account_number = models.CharField(max_length=50)
  bank_name = models.CharField(max_length=100)
  account_name = models.CharField(max_length=100)
  
  def __str__(self):
    return f"{self.shop.name} - {self.bank_name}"
    
    
class Shop_product(models.Model):
  CONDITION_CHOICES = [
    ('new', 'New'),
    ('used', 'Used'),
  ]
  
  shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='shop_products')
  category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='shop_products')
  name = models.CharField(max_length=200)
  description = models.TextField()
  stock = models.PositiveIntegerField(default=0)
  price = models.DecimalField(max_digits=10, decimal_places=2)
  condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='new')
  is_available = models.BooleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return f"{self.name} - {self.shop.name} "
  

class Product(models.Model):
  CONDITION_CHOICES = [
    ('new', 'New'),
    ('used', 'Used')
  ]
  
  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
  category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
  name = models.CharField(max_length=100)
  description = models.TextField()
  price = models.DecimalField(max_digits=10, decimal_places=2)
  stock = models.PositiveIntegerField(default=0)
  condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='new')
  is_deleted = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  def __str__(self):
    return self.name
    
    
class ProductAccountDetail(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='product_account')
  account_number = models.CharField(max_length=100, blank=True)
  bank_name = models.CharField(max_length=100, blank=True)
  account_name = models.CharField(max_length=100, blank=True)
  
    
    
class ProductImage(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, related_name='images')
  shop_product = models.ForeignKey(Shop_product, on_delete=models.CASCADE, null=True, blank=True, related_name='images')
  image = models.ImageField(upload_to='product_images/')
  created_at = models.DateTimeField(auto_now_add=True)
  
  def __str__(self):
    return f"Image for {self.product or self.shop_product}"
    
    
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