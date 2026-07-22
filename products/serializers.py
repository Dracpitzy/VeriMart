from rest_framework import serializers
from .models import Category, Shop, Product, Shop_product, ShopReview, ProductReview, ProductImage

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
      'shop'
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
      
      
class ShopReviewSerializer(serializers.ModelSerializer):
  buyer_name = serializers.CharField(source='buyer.username', read_only=True)
  
  class Meta:
    model = ShopReview
    fields = '__all__'
    read_only_fields = [
      'buyer',
      'created_at'
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
    