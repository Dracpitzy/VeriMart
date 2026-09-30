from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser


phone_regex = RegexValidator(
  regex=r'^(0\d{10}|\+234\d{10})$',
  message='Enter a valid Nigerian phone number (e.g. 08012345678 or +2348012345678).'
)


class user(AbstractUser):
  email = models.EmailField(unique=True)

  REQUIRED_FIELDS = ['email']
  
  def __str__(self):
    return self.username
    
class customer_profile(models.Model):
  user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
  first_name = models.CharField(max_length=20)
  surname = models.CharField(max_length=20, blank=True)
  address = models.TextField()
  shipping_address = models.TextField()
  phone_number = models.CharField(max_length=15, validators=[phone_regex])
  
  def __str__(self):
    return self.user.username
  
  