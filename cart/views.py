from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import (
    AddCartItemSerializer,
    CartSerializer,
    UpdateCartItemQuantitySerializer,
)


class CartDetailView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class CartItemCreateView(APIView):
  permission_classes = [IsAuthenticated]
  
  def post(self, request):
    serializer = AddCartItemSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    item = serializer.save()
    cart = item.cart
    return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
    
    
class CartItemUpdateView(APIView):
  permission_classes = [IsAuthenticated]
  
  def patch(self, request, pk):
    item = CartItem.objects.filter(cart__user=request.user, pk=pk).first()
    if item is None:
      return Response(
        {'error': 'Not found'},
        status=status.HTTP_404_NOT_FOUND
      )
    serializer = UpdateCartItemQuantitySerializer(item, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class CartItemDeleteView(APIView):
  permission_classes = [IsAuthenticated]
  
  def delete(self, request, pk):
    item = CartItem.objects.filter(cart__user=request.user, pk=pk).first()
    
    if item is None:
      return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
      
    item.delete()
    return Response({'message': 'Cart item deleted'}, status=status.HTTP_204_NO_CONTENT)
    
    
class AdminCartsView(APIView):
  permission_classes = [IsAdminUser]
  
  def get(self, request):
    carts = Cart.objects.all()
    serializer = CartSerializer(carts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)