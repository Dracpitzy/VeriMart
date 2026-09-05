from django.urls import path
from .views import (
  CartDetailView, CartItemCreateView, CartItemUpdateView, CartItemDeleteView, AdminCartsView
)


urlpatterns = [
  path('view-cart/', CartDetailView.as_view()),
  path('add-cartitem/', CartItemCreateView.as_view()),
  path('cartitem/<int:pk>/update-quantity/', CartItemUpdateView.as_view()),
  path('cartitem/<int:pk>/delete/', CartItemDeleteView.as_view()),
  path('admin-cart-view/', AdminCartsView.as_view())
]