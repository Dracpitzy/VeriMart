from django.urls import path
from .views import CategoryView, CategoryDetailView, ShopView, ShopDetailView, ScheduleShopDeleteView, ScheduleShopDeleteDetailView, AllShopsView, ShopReviewView, ShopReviewDetailView, Shop_productView, Shop_productDetailView, Shop_productNotAvailableView, Shop_productAvailableView, Shop_productViewUnavailableView, ProductView, ProductDetailView, ProductDeleteSchedule, ViewDeletedProducts, CategoryProductShop_productView


urlpatterns = [
  path('category/', CategoryView.as_view()),
  path('category_detail/<int:id>/', CategoryDetailView.as_view()),
  path('shop/', ShopView.as_view()),
  path('shop_detail/<int:id>/', ShopDetailView.as_view()),
  path('deleted-shops/',ScheduleShopDeleteView.as_view()),
  path('deleted_shops_details/<int:id>/', ScheduleShopDeleteDetailView.as_view()),
  path('all_shops/', AllShopsView.as_view()),
  path('shop_review/<int:shop_id>/', ShopReviewView.as_view()),
  path('shop_detail_review/<int:review_id>/', ShopReviewDetailView.as_view()),
  path('shop_product/<int:shop_id>/', Shop_productView.as_view()),
  path('shop_product_details/<int:id>/', Shop_productDetailView.as_view()),
  path('shop_product_status_not_available/<int:id>/', Shop_productNotAvailableView.as_view()),
  path('shop_product_status_available/<int:id>/', Shop_productAvailableView.as_view()),
  path('view_unavailiable_products/<int:shop_id>/', Shop_productViewUnavailableView.as_view()),
  path('product/', ProductView.as_view()),
  path('product_details/<int:product_id>/', ProductDetailView.as_view()),
  path('deleted_products/<int:product_id>/', ProductDeleteSchedule.as_view()),
  path('view_deleted_product/<int:product_id>/', ViewDeletedProducts.as_view()),
  path('category-products/<int:category_id>/', CategoryProductShop_productView.as_view())
  ]