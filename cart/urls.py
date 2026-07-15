from django.urls import path
from .views import (
  CartDetailView, CartItemCreateView, CartItemUpdateView, CartItemDeleteView,
)


urlpatterns = [
  path('view-cart/', CartDetailView.as_view()),
  path('add-cartitem/', CartItemCreateView.as_view()),
  path('increase-cartitem-quantity/', CartItemUpdateView.as_view()),
  path('delete-cartitem/', CartItemDeleteView.as_view())
]