from rest_framework import serializers
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
  
  product_name = serializers.SerializerMethodField()
  product_image = serializers.SerializerMethodField()
  subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
  
  class Meta:
    model = OrderItem
    fields = ['id', 'product_name', 'product_image', 'quantity', 'price', 'subtotal']
  
  def get_product_name(self, obj):
    if obj.product:
      return obj.product.name
    if obj.shop_product:
      return obj.shop_product.name
      
  def get_product_image(self, obj):
    if obj.product:
      return obj.product.image.url if obj.product.image else None
    if obj.shop_product:
      return obj.shop_product.image.url if obj.shop_product.image else None
    return None
    

class OrderSerializer(serializers.ModelSerializer):
  items = OrderItemSerializer(many=True, read_only=True)
  total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
  status = serializers.CharField(source='get_status_display', read_only=True)
   
  class Meta:
    model = Order
    fields = [
      'id', 'shipping_address', 'total_price', 'items', 'created_at', 'updated_at'
    ]

class CheckoutSerializer(serializers.Serializer):
  shipping_address = serializers.CharField()
  

class AddOrderItemSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = OrderItem
    fields = '__all__'