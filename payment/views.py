from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from orders.models import Order
from .models import Payment, SellerBalance
from .serializers import InitializePaymentSerializer, PaymentSerializer, SellerBalanceSerializer
from . import services


class InitializePaymentView(APIView):
  permission_classes = [IsAuthenticated]
  
  def post(self, request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    serializer = InitializePaymentSerializer(data={}, context={'order': order})
    serializer.is_valid(raise_exception=True)
    payment = serializer.save()
    
    authorization_url = services.initialize_transaction(payment, request.user.email)
    
    return Response(
      {
        'payment': PaymentSerializer(payment).data,
        'authorization_url': authorization_url,
      },
      status=status.HTTP_201_CREATED,
    )
 
    
class PaymentDetailView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request, pk):
    
    payment = get_object_or_404(Payment, pk=pk, order__user=request.user)
    
    serializer = PaymentSerializer(payment)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class MySellerBalanceView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request):
    balance, _ = SellerBalance.objects.get_or_create(seller=request.user)
    serializer = SellerBalanceSerializer(balance)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class AdminSellerBalanceListView(APIView):
  permission_classes = [IsAdminUser]
  
  def get(self, request):
    balances = SellerBalance.objects.all()
    serializer = SellerBalanceSerializer(balances, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class AdminSellerBalancePayoutView(APIView):
  permission_classes = [IsAdminUser]
  
  def patch(self, request, pk):
    balance = get_object_or_404(SellerBalance, pk=pk)
    amount = request.data.get('amount')
    
    if amount is None:
      return Response({'error': 'amount is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
      amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
      return Response({'error': 'amount must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)
    
    if amount <= 0:
      return Response({'error': 'amount must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)
      
    if amount > balance.available:
      return Response({'error': 'amount exceeds available balance'}, status=status.HTTP_400_BAD_REQUEST)
    balance.available -= amount
    balance.withdrawn += amount
    balance.save(update_fields=['available', 'withdrawn', 'updated_at',])
    return Response(SellerBalanceSerializer(balance).data, status=status.HTTP_200_OK)
    
    
class PaymentWebhookView(APIView):
  permission_classes = [AllowAny]
  
  def post(self, request):
    if not services.verify_webhook_signature(request):
      return Response(status=status.HTTP_400_BAD_REQUEST)
      
    if request.data.get('event') != 'charge.success':
      return Response(status=status.HTTP_200_OK)
      
    reference = request.data.get('data', {}).get('reference')
    payment = Payment.objects.filter(transaction_reference=reference).first()
    if payment is None:
      return Response(status=status.HTTP_404_NOT_FOUND)
      
    if payment.status == 'success':
      return Response(status=status.HTTP_200_OK)
    
    verified_data = services.verify_transaction(reference)
    if not verified_data.get('success'):
      payment.status = 'failed'
      payment.gateway_response = verified_data
      payment.save(update_fields=['status', 'gateway_response', 'updated_at'])
      return Response(status=status.HTTP_200_OK)
    
    expected_amount = int(services.calculate_amount_with_fee(payment.amount) * 100)
    if verified_data.get('amount') != expected_amount:
      payment.status = 'failed'
      payment.gateway_response = verified_data
      payment.save(update_fields=['status', 'gateway_response', 'updated_at'])
      return Response(status=status.HTTP_200_OK)
      
    with transaction.atomic():
      payment.status = 'success'
      payment.gateway_response = verified_data
      payment.verified_at = timezone.now()
      payment.save(update_fields=['status', 'gateway_response', 'verified_at', 'updated_at',])
      
      order = payment.order
      order.status = 'paid'
      order.save(update_fields=['status', 'updated_at'])
      
      for item in order.items.all():
        seller = item.product.user if item.product else item.shop_product.shop.owner
        commission = item.subtotal * services.PLATFORM_COMMISSION_RATE
        seller_amount = item.subtotal - commission
        balance, _ = SellerBalance.objects.get_or_create(seller=seller)
        balance.pending += seller_amount
        balance.save(update_fields=['pending', 'updated_at'])
    return Response(status=status.HTTP_200_OK)