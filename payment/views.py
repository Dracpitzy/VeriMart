from decimal import Decimal, InvalidOperation
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
import requests
import logging
from rest_framework.throttling import ScopedRateThrottle

from orders.models import Order
from .models import Payment, SellerBalance, Payout
from .serializers import InitializePaymentSerializer, PaymentSerializer, PayoutSerializer, SellerBalanceSerializer
from . import services
from . import emails

logger = logging.getLogger(__name__)


class InitializePaymentView(APIView):
  permission_classes = [IsAuthenticated]
  throttle_classes = [ScopedRateThrottle]
  throttle_scope = 'payment_initialize'
  
  def post(self, request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    if order.status != 'pending':
      return Response(
        {'error': 'This order cannot be paid for in its current state.'}, status=status.HTTP_400_BAD_REQUEST
      )
    
    serializer = InitializePaymentSerializer(data={}, context={'order': order})
    serializer.is_valid(raise_exception=True)
    payment = serializer.save()
    
    try:
      authorization_url = services.initialize_transaction(payment, request.user.email)
    except requests.RequestException:
      return Response(
        {'error': 'Could not reach the payment gateway. Please try again shortly.'},
        status=status.HTTP_502_BAD_GATEWAY
      )
      
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
    amount = request.data.get('amount')
    note = request.data.get('note', '')
    
    if amount is None:
      return Response({'error': 'amount is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
      amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
      return Response({'error': 'amount must be a valid number'}, status=status.HTTP_400_BAD_REQUEST)
    
    if amount <= 0:
      return Response({'error': 'amount must be greater than zero'}, status=status.HTTP_400_BAD_REQUEST)
      
    with transaction.atomic():
      balance = get_object_or_404(SellerBalance.objects.select_for_update(), pk=pk)
      
      if amount > balance.available:
        return Response({'error': 'amount exceeds available balance'}, status=status.HTTP_400_BAD_REQUEST)
        
      balance.available -= amount
      balance.withdrawn += amount
      balance.save(update_fields=['available', 'withdrawn', 'updated_at',])
      
      Payout.objects.create(
        seller_balance=balance,
        amount=amount,
        processed_by=request.user,
        note=note,
      )
    return Response(
      SellerBalanceSerializer(balance).data, status=status.HTTP_200_OK
    )
    
    
class SellerPayoutHistoryView(APIView):
  permission_classes = [IsAuthenticated]
  
  def get(self, request):
    balance, _ = SellerBalance.get_or_create(seller=request.user)
    payouts = balance.payouts.all().order_by('-created_at')
    serializer = PayoutSerializer(payouts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class AdminPayoutListView(APIView):
  permission_classes = [IsAdminUser]
  
  def get(self, request):
    payouts = Payout.objects.select_related('seller_balance__seller', 'processed_by').order_by('-created_at')
    serializer = PayoutSerializer(payouts, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
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
      
    try:
      verified_data = services.verify_transaction(reference)
    except requests.RequestException:
      return Response(status=status.HTTP_502_BAD_GATEWAY)
    
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
      
    if payment.order.status in ('cancelled', 'delivered'):
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
        balance, _ = SellerBalance.objects.select_for_update().get_or_create(seller=seller)
        balance.pending += seller_amount
        balance.save(update_fields=['pending', 'updated_at'])
        
    confirmation_sent = emails.send_order_confirmation_email(order)
    if not confirmation_sent:
      logger.error(f"Order confirmation email failed to send for Order #{order.id}")
      
    notification_results = emails.send_seller_sale_notifications(order)
    for seller_id, sent in notification_results.items():
      if not sent:
        logger.error(f"Seller sale notification failed for sellar #{seller_id}, Order #{order.id}")
        
    return Response(status=status.HTTP_200_OK)