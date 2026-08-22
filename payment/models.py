from django.db import models
from django.conf import settings
from django.db.models import Q
from orders.models import Order


class Payment(models.Model):
  STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('success', 'Success'),
    ('failed', 'Failed'),
  ]
  
  order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
  transaction_reference = models.CharField(max_length=100, unique=True)
  amount = models.DecimalField(max_digits=10, decimal_places=2)
  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
  geteaway_response = models.JSONField(null=True, blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  verified_at = models.DateTimeField(null=True, blank=True)
  
  class Meta:
    constraints = [
      models.CheckConstraint(
        condition=Q(amount__gt=0),
        name='payment_amount_positives',
      ),
    ]
    
  def __str__(self):
    return f"Payment {self.transaction_reference} for Order #{self.order_id} ({self.status})"
    
    
class SellerBalance(models.Model):
  seller = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='balance')
  pending = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  available = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  withdrawn = models.DecimalField(max_digits=10, decimal_places=2, default=0)
  updated_at = models.DateTimeField(auto_now=True)
  
  class Meta:
    constraints = [
      models.CheckConstraint(condition=Q(pending__gte=0), name='sellerbalance_pending_non_negative'),
      models.CheckConstraint(condition=Q(available__gte=0), name='sellerbalance_available_non_negative'),
      models.CheckConstraint(condition=Q(withdrawn__gte=0), name='sellerbalance_withdrawn_non_negative'),
    ]
    
  def __str__(self):
    return f"{self.seller}'s balance"
    
  @property
  def total_earned(self):
    return self.pending + self.available + self.withdrawn
