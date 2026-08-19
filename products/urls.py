from django.urls import path
from .views import CategoryView, CategoryDetailView, ShopView, ShopDetailView, ScheduleShopDeleteView, ScheduleShopDeleteDetailView, AllShopsView, ShopReviewView, ShopReviewDetailView, Shop_productView, Shop_productDetailView, Shop_productNotAvailableView, Shop_productAvailableView, Shop_productViewUnavailableView, ProductView, ProductDetailView, ProductDeleteSchedule, ViewDeletedProducts, CategoryProductShop_productView, ProductReviewView, ProductReviewDetailView, ProductImageView, ProductImageDetailView, ShopBankDetailView, ShopBankListView, ProductAccountDetailView, ProductAccountListView


urlpatterns = [
  path('category/', CategoryView.as_view()),
  path('category-detail/<int:id>/', CategoryDetailView.as_view()),
  path('shop/', ShopView.as_view()),
  path('shop-detail/<int:id>/', ShopDetailView.as_view()),
  path('deleted-shops/',ScheduleShopDeleteView.as_view()),
  path('deleted-shops-details/<int:id>/', ScheduleShopDeleteDetailView.as_view()),
  path('all-shops/', AllShopsView.as_view()),
  path('shop-review/<int:shop_id>/', ShopReviewView.as_view()),
  path('shop-detail-review/<int:review_id>/', ShopReviewDetailView.as_view()),
  path('shop-product/<int:shop_id>/', Shop_productView.as_view()),
  path('shop-product-details/<int:id>/', Shop_productDetailView.as_view()),
  path('shop-product-status-not-available/<int:id>/', Shop_productNotAvailableView.as_view()),
  path('shop-product-status-available/<int:id>/', Shop_productAvailableView.as_view()),
  path('view-unavailiable-products/<int:shop_id>/', Shop_productViewUnavailableView.as_view()),
  path('product/', ProductView.as_view()),
  path('product-details/<int:product_id>/', ProductDetailView.as_view()),
  path('deleted-products/<int:product_id>/', ProductDeleteSchedule.as_view()),
  path('view-deleted-products/', ViewDeletedProducts.as_view()),
  path('category-products/<int:category_id>/', CategoryProductShop_productView.as_view()),
  path('products/<int:product_id>/reviews/', ProductReviewView.as_view()),
  path('shop-products/<int:shop_product_id>/reviews/', ProductReviewView.as_view()),
  path('reviews/<int:review_id>/', ProductReviewDetailView.as_view()),
  path('delete-product-image/<int:image_id>/', ProductImageDetailView.as_view())
  path('shops/<int:shop_id>/bank-detail/', ShopBankDetailView.as_view()),
  path('shops/bank-details/', ShopBankListView.as_view()),
  path('account-detail/', ProductAccountDetailView.as_view()),
  path('account-details/', ProductAccountListView.as_view()),
  path('products/<int:product_id>/images/', ProductImageView.as_view()),
  path('shop-products/<int:shop_product_id>/images/', ProductImageView.as_view()),
  ]