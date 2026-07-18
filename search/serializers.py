from rest_framework import serializers
from products.models import Category, Shop, Product, Shop_product


class CategorySearchSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Category
    fields = ['id', 'name']
    
    
class ShopSearchSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = Shop
    fields = ['id', 'name', 'description', 'logo']
    

class ProductSearchSerializer(serializers.ModelSerializer):
  
  category_name = serializers.CharField(source='category.name', read_only=True)
  result_type = serializers.SerializerMethodField()
  
  class Meta:
    model = Product
    fields = ['id', 'name', 'description', 'price', 'image', 'category_name', 'result_type']
    
  def get_result_type(self, obj):
    return 'product'
    
    
class ShopProductSearchSerializer(serializers.ModelSerializer):
  category_name = serializers.CharField(source='category.name', read_only=True)
  shop_name = serializers.CharField(source='shop.name', read_only=True)
  result_type = serializers.SerializerMethodField()
  
  class Meta:
    model = Shop_product
    fields = ['id', 'name', 'description', 'price', 'images', 'category_name', 'shop_name', 'result_type']
    
  def get_result_type(self, obj):
    return 'shop_product'
    
    
class ProductSuggestionSerializer(serializers.ModelSerializer):
  result_type = serializers.SerializerMethodField()
  
  class Meta:
    model = Product
    fields = ['id', 'name', 'result_type']
    
  def get_result_type(self, obj):
    return 'product'
    
    
class ShopProductSuggestionSerializer(serializers.ModelSerializer):
  result_type = serializers.SerializerMethodField()
  
  class Meta:
    model = Shop_product
    fields = ['id', 'name', 'result_type']
    
  def get_result_type(self, obj):
    return 'shop_product'