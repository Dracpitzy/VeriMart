from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Category, Shop, Shop_product, Product
from .serializers import CategorySerializer, ShopSerializer, Shop_productSerializer, ProductSerializer


class CategoryView(APIView):
  
  def post(self, request):
    if not request.user.is_staff:
      return Response(
        {'error': 'Only admins can create category'},
        status=status.HTTP_403_FORBIDDEN
        )
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
        )
    return Response(
      serializer.errors,
      status=status.HTTP_400_BAD_REQUEST
      )
      
  def get(self, request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data,
    status=status.HTTP_200_OK
    )
    
class CategoryDetailView(APIView):
  
  def get(self, request, id):
    try:
      category = Category.objects.get(id=id)
    except Category.DoesNotExist:
      return Response(
        {'error': 'Category not found'},
        status=status.HTTP_400_BAD_REQUEST
        )
    serializer = CategorySerializer(category)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
    
  def put(self, request, id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Only admins can edit category'},
        status=status.HTTP_403_FORBIDDEN
        )
    try:
      category = Category.objects.get(id=id)
    except Category.DoesNotExist:
      return Response(
        {'error': 'Category not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    serializer = CategorySerializer(category, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(
        serializer.data,
        status=status.HTTP_200_OK
        )
    return Response(
      serializer.errors,
      status=status.HTTP_400_BAD_REQUEST
      )
    
    
  def delete(self, request, id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Only admins can delete category'},
        status=status.HTTP_403_FORBIDDEN
        )
    try:
      category = Category.objects.get(id=id)
    except Category.DoesNotExist:
      return Response(
        {'error': 'Category not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    category.delete()
    return Response(
      {'message': 'Category deleted'},
      status=status.HTTP_204_NO_CONTENT
      )
      
      
class ShopView(APIView):
  def post(self, request):
    if not request.user.is_authenticated:
      return Response(
        {'error': 'Login to create a shop'},
        status=status.HTTP_403_FORBIDDEN
        )
    serializer = ShopSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(
        serializer.data,
        status=status.HTTP_200_OK
        )
    return Response(
      serializer.error,
      status=status.HTTP_400_BAD_REQUEST
      )
      
  def get(self, request):
    shops = Shop.objects.filter(is_active=True)
    serializer = ShopSerializer(shops, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
    
class ShopDetailView(APIView):
  def get(self, request, id):
    try:
      shop = Shop.objects.get(id=id, is_active=True)
    except Shop.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    serializer = ShopSerializer(shop)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
  def put(self, request, delete):
    if shop.owner != request.user:
      return Response({'error': 'Not your shop'}, status=status.HTTP_403_FORBIDDEN)
    try:
      shop = Shop.objects.get(id=id)
    except Shop.DoesNotExist:
      return Response({'error': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ShopSerializer(shop, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(
        serializer.data,
        status=status.HTTP_200_OK
        )
    return Response(
      serializer.errors,
      status=status.HTTP_400_BAD_REQUEST
      )
      
  def delete(self, request, id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Only admin can delete shop'},
        status=status.HTTP_403_FORBIDDEN
        )
    try:
      shop = Shop.objects.get(id=id)
    except Shop.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_400_BAD_REQUEST
        )
    shop.delete()
    return Response(
      {'message': 'Shop deleted'},
      status=status.HTTP_204_NO_CONTENT
      )
      
    
class ScheduleShopDeleteView(APIView):
  def get(self, request):
    if not request.user.is_staff:
      return Response(
        {'error': 'Accessable to admin only'},
        status=status.HTTP_403_FORBIDDEN
        )
    shops = Shop.objects.filter(is_active=False)
    serializer = ShopSerializer(shops, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
  
  def delete(self, request):
    if not request.user.is_staff:
      return Response(
        {'error': 'Accessable to admin only'},
        status=status.HTTP_403_FORBIDDEN
        )
    shops = Shop.objects.filter(is_active=False)
    result = shops.delete()
    return Response(
      {'message': f'{result} shops deleted'},
      status=status.HTTP_200_OK
      )
      
  
class ScheduleShopDeleteDetailView(APIView):
  def get(self, request, id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Accessable to admin only'},
        status=status.HTTP_403_FORBIDDEN
        )
    try:
      shop = Shop.objects.get(id=id, is_active=False)
    except Shop.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_400_BAD_REQUEST
        )
    serializer = ShopSerializer(shop)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
  def delete(self, request, id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Accessable to admin only'},
        status=status.HTTP_403_FORBIDDEN
        )
    try:
      shop = Shop.objects.get(id=id, is_active=False)
    except Shop.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_400_BAD_REQUEST
        )
    shop.delete()
    return Response(
      {'message': 'Shop deleted'}
      status=status.HTTP_204_NO_CONTENT
      )
      
    
class AllShopsView(APIView):
  def get(self, request):
    if not request.user.is_staff:
      return Response(
        {'error': 'Accessable to admin only'},
        status=status.HTTP_403_FORBIDDEN
        )
    shops = Shop.objects.all()
    serializer = ShopSerilizer(shops, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
