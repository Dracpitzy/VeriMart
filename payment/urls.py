from django.urls import path
from .views import (
  InitializePaymentView,
    PaymentDetailView,
    MySellerBalanceView,
    AdminSellerBalanceListView,
    AdminSellerBalancePayoutView,
    PaymentWebhookView,
)


urlpatterns = [
  path('initialize/<int:order_id>/', InitializePaymentView.as_view()),
  path('payment-detail/<int:pk>/', PaymentDetailView.as_view()),
  path('my-balance/', MySellerBalanceView.as_view()),
  path('admin-balances/', AdminSellerBalanceListView.as_view()),
  path('admin-payout/<int:pk>/', AdminSellerBalancePayoutView.as_view()),
  path('webhook/', PaymentWebhookView.as_view()),
]