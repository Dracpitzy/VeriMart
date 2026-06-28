from rest_framework import serializers
from .models import Category, Shop, Shop_product, Shop_product, ShopReview

class CategorySerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Category
    fields = '__all__'
    
    
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
  buyer_name = serializer.CharField(source='buyer.username', read_only=True)
  
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