from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer, CheckoutSerializer
from cart.models import Cart, CartItem
from products.models import Product, Shop_product


class OrderListCreateView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
  def post(self, request):
    serializer = CheckoutSerializer(data=request.data)
    if not serializer.is_valid():
      return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    if not cart_items.exists():
      return Response(
        {'error': 'Your cart is empty'},
        status=status.HTTP_400_BAD_REQUEST
        )
    with transaction.atomic():
      order = Order.objects.create(
        user=request.user,
        shipping_address=serializer.validated_data['shipping_address']
      )
      for item in cart_items:
        if item.product and item.shop_product:
            return Response(
                {'error': 'Cart item cannot have both a product and a shop product'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not item.product and not item.shop_product:
            return Response(
                {'error': 'Cart item must have either a product or a shop product'},
                status=status.HTTP_400_BAD_REQUEST
            )
        OrderItem.objects.create(
          order=order,
          product=item.product if item.product else None,
          shop_product=item.shop_product if item.shop_product else None,
          quantity=item.quantity,
          price=item.product.price if item.product else item.shop_product.price
        )
      cart_items.delete()
    return Response(
      OrderSerializer(order).data,
      status=status.HTTP_201_CREATED
    )
    
    
class OrderDetailView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    serializer = OrderSerializer(order)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
    )
    
  def patch(self, request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.status != 'shipped':
      return Response(
        {'error': 'You can only confirm delivery after order has been shipped'},
        status=status.HTTP_400_BAD_REQUEST
      )
    order.status = 'delivered'
    order.save()
    return Response(
      OrderSerializer(order).data,
      status=status.HTTP_200_OK
    )
 
    
class AdminOrderListView(APIView):
  permission_classes = [IsAdminUser]
  
  def get(self, request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
    )
    
    
class AdminOrderListDetailView(APIView):
  permission_classes = [IsAdminUser]
  
  def get(self, request, pk):
    order = get_object_or_404(Order, pk=pk)
    serializer = OrderSerializer(order)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
    )
    
    
class AdminUpdateOrderView(APIView):
  permission_classes = [IsAdminUser]
  
  def patch(self, request, pk):
    order = get_object_or_404(Order, pk=pk)
    new_status = request.data.get('status')
    if new_status not in dict(Order.STATUS_CHOICES):
      return Response(
        {'error': 'Invalid status'},
        status=status.HTTP_400_BAD_REQUEST
      )
    order.status = new_status
    order.save()
    serializer = OrderSerializer(order)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
  
class AddOrderItemView(APIView):
  permission_classes = [IsAuthenticated]
  
  def post(self, request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    if order.status != 'pending':
      return Response(
        {'error': 'You can only add item to an order that is pending'},
        status=status.HTTP_400_BAD_REQUEST
      )
    product_id = request.data.get('product_id')
    shop_product_id = request.data.get('shop_product_id')
    quantity = request.data.get('quantity', 1)
    
    if not product_id and not shop_product_id:
      return Response(
        {'error': 'Either product_id or shop_product_id is required'},
        status=status.HTTP_400_BAD_REQUEST
      )
    if product_id and shop_product_id:
      return Response(
        {'error': 'You can only add one product type at a time'},
        status=status.HTTP_400_BAD_REQUEST
      )
    
    if product_id:
      product = get_object_or_404(Product, pk=product_id)
      existing_item = OrderItem.objects.filter(order=order, product=product).first()
      if existing_item:
        existing_item.quantity += quantity
        existing_item.save()
      else:
        OrderItem.objects.create(
          order=order,
          product=product,
          quantity=quantity,
          price=product.price
        )
        
    if shop_product_id:
      shop_product = get_object_or_404(Shop_product, pk=shop_product_id)
      existing_item = OrderItem.objects.filter(order=order, shop_product=shop_product).first()
      if existing_item:
        existing_item.quantity += quantity
        existing_item.save()
      else:
        OrderItem.objects.create(
          order=order,
          shop_product=shop_product,
          quantity=quantity,
          price=shop_product.price
        )
      
    return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)
    