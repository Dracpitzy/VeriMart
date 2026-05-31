from django.db import models
from users.views import user

class cart(models.Model):
  user = models.ForeignKey(user, on_delete=CASCADE)
  
  def __str__(self):
    return self.user.username
  
