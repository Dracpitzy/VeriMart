from rest_framework import serializers
from .models import Category, Shop, Product, Shop_product, ShopReview, ProductReview, ProductImage, ShopBankDetail, ProductAccountDetail

class CategorySerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Category
    fields = '__all__'
    
    
class ProductImageSerializer(serializers.ModelSerializer):
  class Meta:
    model = ProductImage
    fields = ['id', 'product', 'shop_product', 'image', 'created_at']
    read_only_fields = ['product', 'shop_product', 'created_at']
    
    
class ShopSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Shop
    fields = '__all__'
    read_only_fields = [
      'created_at',
      'updated_at',
      'owner',
      ]
    
    
class Shop_productSerializer(serializers.ModelSerializer):
  category_name = serializers.CharField(source='category.name', read_only=True)
  shop_name = serializers.CharField(source='shop.name', read_only=True)
  images = ProductImageSerializer(many=True, read_only=True)
  
  class Meta:
    model = Shop_product
    fields = '__all__'
    read_only_fields = [
      'created_at',
      'updated_at',
      'shop',
      'is_available'
      ]
      
  def validate_condition(self, value):
    if value not in ('new', 'used'):
      raise serializers.ValidationError("Condition must be 'new' or 'used' ")
    return value
    
  
class ProductSerializer(serializers.ModelSerializer):
  category_name = serializers.CharField(source='category.name', read_only=True)
  images = ProductImageSerializer(many=True, read_only=True)
  
  class Meta:
    model = Product
    fields = '__all__'
    read_only_fields = [
      'created_at',
      'updated_at',
      'user',
      'is_deleted'
      ]
      
  def validate_condition(self, value):
    if value not in ('new', 'used'):
      raise serializers.ValidationError("Condition must be 'new' or 'used' ")
    return value
      
      
class ShopReviewSerializer(serializers.ModelSerializer):
  buyer_name = serializers.CharField(source='buyer.username', read_only=True)
  
  class Meta:
    model = ShopReview
    fields = '__all__'
    read_only_fields = [
      'buyer',
      'created_at',
      'is_deleted'
    ]
  def validate_rating(self, value):
    if value < 1 or value > 5:
      raise serializers.ValidationError("Rating must be between 1 and 5")
    return value
      
    
class ProductReviewSerializer(serializers.ModelSerializer):
  buyer_name = serializers.CharField(source='buyer.username', read_only=True)
  
  class Meta:
    model = ProductReview
    fields = [
      'id', 'product', 'shop_product', 'buyer', 'buyer_name', 'rating', 'comment', 'is_deleted', 'created_at'
    ]
    read_only_fields = [
      'buyer', 'created_at', 'is_deleted'
    ]
    
  def validate_rating(self, value):
    if value < 1 or value > 5:
      raise serializers.ValidationError("Rating must be between 1 and 5")
    return value
    
  def validate(self, data):
    if not data.get('product') and not data.get('shop_product'):
      raise serializers.ValidationError("A review must belong to either a product or a shop product.")
    if data.get('product') and data.get('shop_product'):
      raise serializers.ValidationError("A review cannot belong to both a product and a shop product.")
    return data
    
    
class ShopBankDetailSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = ShopBankDetail
    fields = '__all__'
    read_only_fields = ['shop']
    
    
class ProductAccountDetailSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = ProductAccountDetail
    fields = '__all__'
    read_only_fields = ['user']
    
    
class ShopBankListSerializer(serializers.ModelSerializer):
  
  shop_name = serializers.CharField(source='shop.name', read_only=True)
  
  class Meta:
    model = ShopBankDetail
    fields = ['id', 'bank_name', 'account_number', 'account_name', 'shop_name']
    read_only_fields = ['id', 'bank_name', 'account_number', 'account_name', 'shop_name']
    
    
class ProductAccountListSerializer(serializers.ModelSerializer):
  user_name = serializers.CharField(source='user.username', read_only=True)
  
  class Meta:
    model = ProductAccountDetail
    fields = ['id', 'account_number', 'account_name', 'bank_name', 'user_name']
    read_only_fields = ['id', 'account_number', 'account_name', 'bank_name', 'user_name']