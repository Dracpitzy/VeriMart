import uuid
from rest_framework import serializers
from .models import Payment, SellerBalance, Payout


class InitializePaymentSerializer(serializers.Serializer):
  
  def validate(self, attrs):
    order = self.context['order']
    if order.payments.filter(status='success').exists():
      raise serializers.ValidationError('This order has been paid for.')
    return attrs
  
  def create(self, validated_data):
    order = self.context['order']
    existing_pending = order.payments.filter(status='pending').order_by('-created_at').first()
    if existing_pending:
      return existing_pending
      
    payment = Payment.objects.create(
      order=order,
      transaction_reference=uuid.uuid4().hex,
      amount=order.total_price,
    )
    return payment
    
    
class PaymentSerializer(serializers.ModelSerializer):
  order_id = serializers.IntegerField(source='order.id', read_only=True)
  
  class Meta:
    model = Payment
    fields = ['id', 'order_id', 'transaction_reference', 'amount', 'status', 'created_at', 'verified_at', ]
    read_only_fields = fields
    
    
class SellerBalanceSerializer(serializers.ModelSerializer):
  
  shop_name = serializers.SerializerMethodField()
  seller_username = serializers.CharField(source='seller.username', read_only=True)
  total_earned = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
  
  def get_shop_name(self, obj):
    return obj.seller.shop.name if hasattr(obj.seller, 'shop') else None
  
  class Meta:
    model = SellerBalance
    fields = [
      'id', 'seller_username', 'pending', 'available', 'shop_name', 'withdrawn', 'total_earned', 'updated_at',
    ]
    read_only_fields = fields
    
    
class PayoutSerializer(serializers.ModelSerializer):
  
  seller_username = serializers.CharField(source='seller_balance.seller.username', read_only=True)
  processed_by_username = serializers.CharField(source='processed_by.username', read_only=True, default=None)
  
  class Meta:
    model = Payout
    fields = [
      'id', 'seller_username', 'amount',
      'processed_by_username', 'note',
      'created_at'
    ]
    read_only_fields = fields