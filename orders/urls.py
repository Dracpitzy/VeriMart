from django.urls import path
from .views import OrderListCreateView, OrderDetailView, AdminOrderListView, AdminOrderListDetailView, AdminUpdateOrderView, AddOrderItemView

urlpatterns = [
  path('create-view-order/', OrderListCreateView.as_view()),
  path('order-detail/<int:pk>/', OrderDetailView.as_view()),
  path('admin-order-view/', AdminOrderListView.as_view()),
  path('admin-order-view-detail/<int:pk>/', AdminOrderListDetailView.as_view()),
  path('update-order/<int:pk>/', AdminUpdateOrderView.as_view()),
  path('add-item-order/<int:pk>/', AddOrderItemView.as_view())
]