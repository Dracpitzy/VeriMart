from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer, CheckoutSerializer
from cart.models import Cart, CartItem
from products.models import Product, Shop_product
from payment.services import release_pending_to_available
from payment.models import SellerBalance
from products.services import update_verification_status
from .services import reserve_order_stock, release_order_stock, mark_order_delivered, InsufficientStock


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
    cart_items = CartItem.objects.filter(cart=cart).select_related('product', 'shop_product__shop')
    if not cart_items.exists():
      return Response(
        {'error': 'Your cart is empty'},
        status=status.HTTP_400_BAD_REQUEST
        )
        
    for item in cart_items:
      if item.product and item.shop_product:
        return Response(
          {'error': 'Cart item cannot have both a product and a shop product'}, status=status.HTTP_400_BAD_REQUEST
        )
      if not item.product and not item.shop_product:
        return Response(
          {'error': 'Cart item must have either a product or a shop product'}, status=status.HTTP_400_BAD_REQUEST
        )
        
    problems = []
    priced_items = []
    for item in cart_items:
      target = item.product or item.shop_product
      
      if item.product and item.product.is_deleted:
        problems.append(f'{target.name} is no longer available')
        continue
      if item.shop_product and not item.shop_product.is_available:
        problems.append(f'{target.name} is no longer available')
        continue
      if item.shop_product and not item.shop_product.shop.is_active:
        problems.append(f'{target.name} is from a shop that is currently inactive')
        continue
      if target.stock == 0:
        problems.append(f'{target.name} is out of stock')
        continue
      if item.quantity > target.stock:
        problems.append(f'Only {target.stock} of {target.name} left in stock')
        continue
      
      priced_items.append((item, item.price))
      
      if problems:
        return Response({'error': problems}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
      with transaction.atomic():
        order = Order.objects.create(
          user=request.user,
          shipping_address=serializer.validated_data['shipping_address']
        )
        
        for item, price in priced_items:
          OrderItem.objects.create(
            order=order,
            product=item.product,
            shop_product=item.shop_product,
            quantity=item.quantity,
            price=price
          )
        reserved_order_stock(order)
        cart_items.delete()
    except InsufficientStock as error:
      return Response(
        {'error': [f'{error.name} just ran out of stock']},
        status=status.HTTP_400_REQUEST
      )
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
      
    try:
      delivered = mark_order_delivered(order)
    except SellerBalance.DoesNotExist:
      return Response(
        {'error': 'Could not release funds - a seller balance record is missing. Please contact support.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )
    if not delivered:
      return Response(
        {'error': 'This order can no longer be confirmed as delivered'},
        status=status.HTTP_400_BAD_REQUEST
      )
      
    return Response(
      OrderSerializer(order).data,
      status=status.HTTP_200_OK
    )
 
    
class AdminOrderListView(APIView):
  permission_classes = [IsAdminUser]
  
  def get(self, request):
    orders = Order.objects.prefetch_related('items').all()
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
    if new_status == 'paid':
      return Response(
        {'error': 'Orders can only be marked paid by the payment flow'},
        status=status.HTTP_400_BAD_REQUEST
      )
      
    if new_status == 'cancelled' and order.status != 'pending':
      return Response(
        {'error': 'Only pending orders can be cancelled. Cancelling a paid order needs a refund, which is not supported yet.'},
        status=status.HTTP_400_BAD_REQUEST
      )
      
    if new_status == 'delivered':
      try:
        delivered = mark_order_delivered(order)
      except SellerBalance.DoesNotExist:
        return Response(
          {'error': 'Could not release funds - a seller balance record is missing. Please contact support.'},
          status=status.HTTP_500_INTERNAL_SERVER_ERROR
       )
      if not delivered:
        return Response(
          {'erro': 'Only paid, processing or shipped orders can be marked delivered'},
          status=status.HTTP_400_BAD_REQUEST
        )
      return Response(OrderSerializer(Order).data, status=status.HTTP_200_OK)
      
    previous_status = order.status
    fields_to_save = ['status', 'updated_at']
      
    with transaction.atomic():
      order.status = new_status
      if new_status == 'shipped' and previous_status != 'shipped':
        order.shipped_at = timezone.now()
        fields_to_save.append('shipped_at')
      order.save(update_fields=fields_to_save)
      if new_status == 'cancelled':
        release_order_stock(order)
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
    try:
      quantity = int(request.data.get('quantity', 1))
    except (TypeError, ValueError):
      return Response({'error': 'Quantity must be a valid integer'}, status=status.HTTP_400_BAD_REQUEST)
    if quantity < 1:
      return Response({'error': 'Quantity must be at least 1.'}, status=status.HTTP_400_BAD_REQUEST)
    
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
    