from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Category(models.Model):
  name = models.CharField(max_length=100, unique=True)
  
  def __str__(self):
    return self.name
    
  
class Shop(models.Model):
  owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shop')
  name = models.CharField(max_length=200, unique=True)
  description = models.TextField()
  logo = models.ImageField(upload_to='shops/logos/')
  is_active = models.BoleanField(default=True)
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
  images = models.ImageField(upload_to='shop_products/')
  is_available = models.BoleanField(default=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  
  def __str__(self):
    return f"{self.name} - {self.shop.name} "
  

class Product(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product')
  category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
  name = models.CharField(max_length=100)
  description = models.TextField()
  price = models.DecimalField(max_digits=10, decimal_places=2)
  stock = models.PositiveIntegerField(default=0)
  image = models.ImageField(upload_to='products/')
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  def __str__(self):
    return self.name
  
