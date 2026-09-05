from rest_framework.views import APIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
from products.models import Category, Shop, Product, Shop_product
from .serializers import (
  ProductSearchSerializer,
  ShopProductSearchSerializer,
  CategorySearchSerializer,
  ShopSearchSerializer,
  ProductSuggestionSerializer,
  ShopProductSuggestionSerializer,
)

SUGGESTION_LIMIT = 5

class ProductSearchView(APIView):
  
  def get(self, request):
    query = request.query_params.get('q', '').strip()
    
    if not query:
      return Response({'error': 'Provide a search term using the "q" query parameter.'}, status=status.HTTP_400_BAD_REQUEST)
      
    products = Product.objects.filter(
      Q(name__icontains=query) | Q(description__icontains=query), is_deleted=False
    )
    shop_products = Shop_product.objects.filter(
      Q(name__icontains=query) | Q(description__icontains=query),
      is_available=True
    )
    
    product_results = ProductSearchSerializer(products, many=True).data
    shop_product_results = ShopProductSearchSerializer(shop_products, many=True).data
    
    combined_results = list(product_results) + list(shop_product_results)
    
    return Response(combined_results, status=status.HTTP_200_OK)
    
    
class CategorySearchView(APIView):
  def get(self, request):
    query = request.query_params.get('q', '').strip()
    
    if not query:
      return Response({'error': 'Provide a search term using the "q" query parameter.'}, status=status.HTTP_400_BAD_REQUEST)
      
    categories = Category.objects.filter(
      name__icontains=query
    )
    serializer = CategorySearchSerializer(categories, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class ShopSearchView(APIView):
  def get(self, request):
    query = request.query_params.get('q', '').strip()
    if not query:
      return Response({'error': 'Provide a search term using the "q" query parameter.'}, status=status.HTTP_400_BAD_REQUEST)
    shops = Shop.objects.filter(
      Q(name__icontains=query) | Q(description__icontains=query),
      is_active=True
    )
    
    serializer = ShopSearchSerializer(shops, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class SearchSuggestionView(APIView):
  
  def get(self, request):
    query = request.query_params.get('q', '').strip()
    
    if not query:
      return Response([], status=status.HTTP_200_OK)
    
    products = Product.objects.filter(
      name__icontains=query,
      is_deleted=False
    )[:SUGGESTION_LIMIT]
    
    shop_products = Shop_product.objects.filter(
      name__icontains=query,
      is_available=True
    )[:SUGGESTION_LIMIT]
    
    product_suggestions = ProductSuggestionSerializer(products, many=True).data
    shop_product_suggestions = ShopProductSuggestionSerializer(shop_products, many=True).data
    
    combined_suggestions = list(product_suggestions) + list(shop_product_suggestions)
    
    return Response(combined_suggestions, status=status.HTTP_200_OK)
    
    