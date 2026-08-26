from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
  product_name = serializers.SerializerMethodField()
  subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
  
  class Meta:
    model = CartItem
    fields = [
      'id', 'product_name', 'quantity', 'price', 'subtotal'
    ]
    read_only_fields = ['price']
    
  def get_product_name(self, obj):
    if obj.product:
      return obj.product.name
    if obj.shop_product:
      return obj.shop_product.name


class CartSerializer(serializers.ModelSerializer):
  
  items = CartItemSerializer(many=True, read_only=True)
  total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
  
  class Meta:
    model = Cart
    fields = ['id', 'user', 'items', 'total_price']
    read_only_fields = ['user']
    
    
class AddCartItemSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = CartItem
    fields = ['id', 'product', 'shop_product', 'quantity']
    
  def validate_quantity(self, value):
    if value < 1:
      raise serializers.ValidationError('Quantity must be at least one')
    if value > 5:
      raise serializers.ValidationError('You cannot add more than 5 of the same item')
    return value
    
  def validate(self, attrs):
    product = attrs.get('product')
    shop_product = attrs.get('shop_product')
    quantity = attrs.get('quantity')
    
    if product and shop_product:
      raise serializers.ValidationError("A cart item cannot reference both a product and a shop_product")
    if not product and not shop_product:
      raise serializers.ValidationError("A cart item must reference either a product or a shop product")
      
    request = self.context['request']
    cart, _ = Cart.objects.get_or_create(user=request.user)
    existing = CartItem.objects.filter(cart=cart, product=product, shop_product=shop_product).first()
    current_quantity = existing.quantity if existing else 0
    total_quantity = current_quantity + quantity
    if total_quantity > 5:
      raise serializers.ValidationError('You cannot have more than 5 of the same item in your cart')
      
    target = product or shop_product
    stock = getattr(target, 'stock', None)
    if stock is not None and total_quantity > stock:
      raise serializers.ValidationError(f'Only {stock} left in stock')
      
    return attrs
    
  def create(self, validated_data):
    request = self.context['request']
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    product = validated_data.get('product')
    shop_product = validated_data.get('shop_product')
    quantity = validated_data['quantity']
    
    existing = CartItem.objects.filter(cart=cart, product=product, shop_product=shop_product).first()
    if existing:
      existing.quantity += quantity
      existing.save(update_fields=["quantity"])
      return existing
    
    price = product.price if product else shop_product.price
    return CartItem.objects.create(cart=cart, product=product, shop_product=shop_product, quantity=quantity, price=price)
    
    
class UpdateCartItemQuantitySerializer(serializers.ModelSerializer):
  
  class Meta:
    model = CartItem
    fields = ['quantity']
    
  def validate_quantity(self, value):
    if value < 1:
      raise serializers.ValidationError('Quantity must be atleast 1.')
    if value > 5:
      raise serializers.ValidationError('You cannot add more than 5 of the same item')
      
    item = self.instance
    product = item.product or item.shop_product
    stock = getattr(product, 'stock', None)
    if stock is not None and value > stock:
      raise serializers.ValidationError(f'Only {stock} left in stock')
    
    return value