from rest_framework import serializers
from .models import Category, Shop, Shop_product, Shop_product

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
      'updated_at'
      ]
    
    
class Shop_productSerializer(serializers.ModelSerializer):
  category_name = serializers.CharField(source='category.name', read_only=True)
  shop_name = serializers.CharField(source='shop.name', read_only=True)
  
  class Meta:
    model = Shop_product
    fields = '__all__'
    read_only_fields = [
      'created_at',
      'updated_at'
      ]
    
  
class ProductSerializer(serializers.ModelSerializer):
  category_name = serializers.CharField(source='category.name', read_only=True)
  
  class Meta:
    model = Product
    fields = '__all__'
    read_only_fields = [
      'created_at',
      'updated_at'
      ]