from django.urls import path
from .views import ProductSearchView, CategorySearchView, ShopSearchView, SearchSuggestionView

urlpatterns = [
  path('products/', ProductSearchView.as_view(), name='search-products'),
  path('categories/', CategorySearchView.as_view(), name='search-categories'),
  path('shop/', ShopSearchView.as_view(), name='search-shops'),
  path('suggestions/', SearchSuggestionView.as_view(), name='search-suggestions')
]