from django.db import models
from django.contrib.auth.models import AbstractUser


class user(AbstractUser):
  email = models.EmailField(unique=True)

  REQUIRED_FIELDS = ['email']
  
  def __str__(self):
    return self.username
    
class customer_profile(models.Model):
  user = models.OneToOneField(user, on_delete=models.CASCADE)
  first_name = models.CharField(max_length=20)
  surname = models.CharField(max_length=20, blank=True)
  address = models.TextField()
  shipping_address = models.TextField()
  phone_number = models.CharField(max_length=11)
  
  def __str__(self):
    return self.user.username
  
  