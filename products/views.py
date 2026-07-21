from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Category, Shop, Shop_product, Product, ShopReview, ProductReview
from .serializers import CategorySerializer, ShopSerializer, Shop_productSerializer, ProductSerializer, ShopReviewSerializer, ProductReviewSerializer
from orders.models import Order

class CategoryView(APIView):
  
  def post(self, request):
    if not request.user.is_staff:
      return Response(
        {'error': 'Only admins can create category'},
        status=status.HTTP_403_FORBIDDEN
        )
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
        )
    return Response(
      serializer.errors,
      status=status.HTTP_400_BAD_REQUEST
      )
      
  def get(self, request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data,
    status=status.HTTP_200_OK
    )
    
class CategoryDetailView(APIView):
  
  def get(self, request, id):
    try:
      category = Category.objects.get(id=id)
    except Category.DoesNotExist:
      return Response(
        {'error': 'Category not found'},
        status=status.HTTP_400_BAD_REQUEST
        )
    serializer = CategorySerializer(category)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
    
  def put(self, request, id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Only admins can edit category'},
        status=status.HTTP_403_FORBIDDEN
        )
    try:
      category = Category.objects.get(id=id)
    except Category.DoesNotExist:
      return Response(
        {'error': 'Category not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    serializer = CategorySerializer(category, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(
        serializer.data,
        status=status.HTTP_200_OK
        )
    return Response(
      serializer.errors,
      status=status.HTTP_400_BAD_REQUEST
      )
    
  def delete(self, request, id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Only admins can delete category'},
        status=status.HTTP_403_FORBIDDEN
        )
    try:
      category = Category.objects.get(id=id)
    except Category.DoesNotExist:
      return Response(
        {'error': 'Category not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    category.delete()
    return Response(
      {'message': 'Category deleted'},
      status=status.HTTP_204_NO_CONTENT
      )
      
      
class ShopView(APIView):
  def post(self, request):
    if not request.user.is_authenticated:
      return Response(
        {'error': 'Login to create a shop'},
        status=status.HTTP_403_FORBIDDEN
        )
    serializer = ShopSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(owner=request.user)
      return Response(
        serializer.data,
        status=status.HTTP_200_OK
        )
    return Response(
      serializer.errors,
      status=status.HTTP_400_BAD_REQUEST
      )
      
  def get(self, request):
    shops = Shop.objects.filter(is_active=True)
    serializer = ShopSerializer(shops, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
    
class ShopDetailView(APIView):
  def get(self, request, id):
    try:
      shop = Shop.objects.get(id=id, is_active=True)
    except Shop.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    serializer = ShopSerializer(shop)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
  def put(self, request, id):
    try:
      shop = Shop.objects.get(id=id)
    except Shop.DoesNotExist:
      return Response({'error': 'Shop not found'}, status=status.HTTP_404_NOT_FOUND)
    if shop.owner != request.user:
      return Response({'error': 'Not your shop'}, status=status.HTTP_403_FORBIDDEN)
    serializer = ShopSerializer(shop, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(
        serializer.data,
        status=status.HTTP_200_OK
        )
    return Response(
      serializer.errors,
      status=status.HTTP_400_BAD_REQUEST
      )
      
  def delete(self, request, id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Only admin can delete shop'},
        status=status.HTTP_403_FORBIDDEN
        )
    try:
      shop = Shop.objects.get(id=id)
    except Shop.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_400_BAD_REQUEST
        )
    shop.delete()
    return Response(
      {'message': 'Shop deleted'},
      status=status.HTTP_204_NO_CONTENT
      )
      
    
class ScheduleShopDeleteView(APIView):
  def get(self, request):
    if not request.user.is_staff:
      return Response(
        {'error': 'Accessable to admin only'},
        status=status.HTTP_403_FORBIDDEN
        )
    shops = Shop.objects.filter(is_active=False)
    serializer = ShopSerializer(shops, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
 
'''
 def delete(self, request):
    if not request.user.is_staff:
      return Response(
        {'error': 'Accessable to admin only'},
        status=status.HTTP_403_FORBIDDEN
        )
    shops = Shop.objects.filter(is_active=False)
    result = shops.delete()
    return Response(
      {'message': f'{result[0]} shops deleted'},
      status=status.HTTP_200_OK
      )
'''     
  
class ScheduleShopDeleteDetailView(APIView):
  def get(self, request, id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Accessable to admin only'},
        status=status.HTTP_403_FORBIDDEN
        )
    try:
      shop = Shop.objects.get(id=id, is_active=False)
    except Shop.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_400_BAD_REQUEST
        )
    serializer = ShopSerializer(shop)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
  def delete(self, request, id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Accessable to admin only'},
        status=status.HTTP_403_FORBIDDEN
        )
    try:
      shop = Shop.objects.get(id=id, is_active=False)
    except Shop.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_400_BAD_REQUEST
        )
    shop.delete()
    return Response(
      {'message': 'Shop deleted'},
      status=status.HTTP_204_NO_CONTENT
      )
      
    
class AllShopsView(APIView):
  def get(self, request):
    if not request.user.is_staff:
      return Response(
        {'error': 'Accessable to admin only'},
        status=status.HTTP_403_FORBIDDEN
        )
    shops = Shop.objects.all()
    serializer = ShopSerializer(shops, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )


class ShopReviewView(APIView):
  def post(self, request, shop_id):
    if not request.user.is_authenticated:
      return Response(
        {'error': 'Login to rate shops'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    try:
      shop = Shop.objects.get(id=shop_id)
    except Shop.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    if shop.owner == request.user:
      return Response(
        {'error': 'You can not review your own shop'},
        status=status.HTTP_403_FORBIDDEN
        )
    has_bought = Order.objects.filter(buyer=request.user, items__product__shop=shop).exists()
    if not has_bought:
      return Response(
        {'error': 'You must purchase from this shop before reviewing'},
        status=status.HTTP_403_FORBIDDEN
        )
    if ShopReview.objects.filter(buyer=request.user, shop=shop).exists():
      return Response(
        {'error': 'You can not review a store multiple times'},
        status=status.HTTP_400_BAD_REQUEST
        )
    serializer = ShopReviewSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(shop=shop, buyer=request.user)
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
  def get(self, request, shop_id):
    reviews = ShopReview.objects.filter(shop__id=shop_id, is_deleted=False)
    serializer = ShopReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
  def delete(self, request, shop_id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Only admin can perform this action'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    reviews = ShopReview.objects.filter(shop__id=shop_id, is_deleted=True)
    reviews.delete()
    return Response(
      {'message':'Reviews deleted'},
      status=status.HTTP_204_NO_CONTENT
      )
    
    
class ShopReviewDetailView(APIView):
  def get(self, request, review_id):
    try:
      review = ShopReview.objects.get(id=review_id, is_deleted=False)
    except ShopReview.DoesNotExist:
      return Response(
        {'error': 'Review not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    serializer = ShopReviewSerializer(review)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
  def put(self, request, review_id):
    try:
      review = ShopReview.objects.get(id=review_id)
    except ShopReview.DoesNotExist:
      return Response({'error': 'Review not found'}, status=status.HTTP_403_FORBIDDEN)
    if review.buyer != request.user:
      return Response(
        {'error': 'Not your review'},
        status=status.HTTP_403_FORBIDDEN
        )
    review.is_deleted = True
    review.save()
    return Response({'message': 'Review deleted'}, status=status.HTTP_200_OK)
    
    
class Shop_productView(APIView):
  
  def post(self, request, shop_id):
    if not request.user.is_authenticated:
      return Response(
        {'error': 'Login required'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    try:
      shop = Shop.objects.get(id=shop_id)
    except Shop.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    if shop.owner != request.user:
      return Response(
        {'error': 'Only the shop owner can create product'},
        status=status.HTTP_403_FORBIDDEN
        )
    serializer = Shop_productSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(shop=shop)
      return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
        )
    return Response(
      serializer.errors,
      status=status.HTTP_400_BAD_REQUEST
      )
      
  def get(self, request, shop_id):
    shop_products = Shop_product.objects.filter(shop__id=shop_id, is_available=True)
    serializer = Shop_productSerializer(shop_products, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
      
class Shop_productDetailView(APIView):
  def get(self, request, id):
    try:
      product = Shop_product.objects.get(id=id, is_available=True)
    except Shop_product.DoesNotExist:
      return Response(
        {'error': 'product not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    serializer = Shop_productSerializer(product)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
  def put(self, request, id):
    try:
      product = Shop_product.objects.get(id=id, is_available=True)
    except Shop_product.DoesNotExist:
      return Response(
        {'error': 'Product not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    if product.shop.owner != request.user:
      return Response(
        {'error': 'Only Shop owners can edit product'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    serializer = Shop_productSerializer(product, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(
      serializer.errors,
      statua=status.HTTP_400_BAD_REQUEST
      )
    
  def delete(self, request, id):
    try:
      product = Shop_product.objects.get(id=id)
    except Shop_product.DoesNotExist:
      return Response(
        {'error':'Product not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    if product.shop.owner != request.user and not request.user.is_staff:
      return Response(
        {'error':'Not authorized'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    product.delete()
    return Response(
      {'message':'Shop product deleted'},
      status=status.HTTP_204_NO_CONTENT
      )
      
      
class Shop_productNotAvailableView(APIView):
  def put(self, request, id):
    try:
      product = Shop_product.objects.get(id=id, is_available=True)
    except Shop_product.DoesNotExist:
      return Response(
        {'error': 'Product not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    if product.shop.owner != request.user:
      return Response(
        {'error':'Not authorized'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    product.is_available = False
    product.save()
    return Response(
      {'message': 'Product not available'},
      status=status.HTTP_200_OK
      )
    
  
class Shop_productAvailableView(APIView):
  def put(self, request, id):
    try:
      product = Shop_product.objects.get(id=id)
    except Shop_product.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    if product.shop.owner != request.user:
      return Response(
        {'error': 'Not authorized'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    product.is_available = True
    product.save()
    return Response(
      {'message': 'Product available'}
      )
      
        
class Shop_productViewUnavailableView(APIView):
  def get(self, request, shop_id):
    try:
      shop = Shop.objects.get(id=shop_id)
    except Shop.DoesNotExist:
      return Response(
        {'error': 'Shop not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    if shop.owner != request.user:
      return Response(
        {'error': 'Not your shop'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    unavailable_products = Shop_product.objects.filter(shop__id=shop_id, is_available=False)
    serializer = Shop_productSerializer(unavailable_products, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
    
    
class ProductView(APIView):
  def post(self, request):
    if not request.user.is_authenticated:
      return Response(
        {'error': 'Login to create product'},
        status=status.HTTP_403_FORBIDDEN
        )
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(user=request.user)
      return Response(
        serializer.data,
        status=status.HTTP_201_CREATED
        )
    return Response(
      serializer.errors,
      status=status.HTTP_400_BAD_REQUEST
      )
      
  def get(self, request):
    products = Product.objects.filter(is_deleted=False)
    serializer = ProductSerializer(products, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
  
class ProductDetailView(APIView):
  def get(self, request, product_id):
    try:
      product = Product.objects.get(id=product_id, is_deleted=False)
    except Product.DoesNotExist:
      return Response(
        {'error': 'product not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProductSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
  def put(self, request, product_id):
    try:
      product = Product.objects.get(id=product_id, is_deleted=False)
    except Product.DoesNotExist:
      return Response(
        {'error': 'Product not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    if product.user != request.user and not request.user.is_staff:
      return Response(
        {'error': 'Only Product owner can perform this action'},
        status=status.HTTP_403_FORBIDDEN
        )
    serializer = ProductSerializer(product, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(
        serializer.data,
        status=status.HTTP_200_OK
        )
    return Response(
      serializer.errors,
      status=status.HTTP_400_BAD_REQUEST
      )
    
  def delete(self, request, product_id):
    if not request.user.is_staff:
      return Response(
        {'error': 'You are not authorized to perform this action'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    try:
      product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
      return Response(
        {'error': 'Product not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    product.delete()
    return Response(
      {'message': 'Product deleted'},
      status=status.HTTP_204_NO_CONTENT
      )
    
    
class ProductDeleteSchedule(APIView):
  def put(self, request, product_id):
    try:
      product = Product.objects.get(id=product_id, is_deleted=False)
    except Product.DoesNotExist:
      return Response(
        {'error': 'Product not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    if product.user != request.user:
      return Response(
        {'error': 'You are not authorized to perform this action'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    product.is_deleted = True
    product.save()
    return Response(
      {'message': 'Product removed'},
      status=status.HTTP_200_OK
      )
      
  def get(self, request, product_id):
    if not request.user.is_staff:
      return Response(
        {'error': 'Unauthorized to perform this action'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    try:
      product = Product.objects.get(id=product_id, is_deleted=True)
    except Product.DoesNotExist:
      return Response(
        {'error': 'Product not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    serializer = ProductSerializer(data=request.data)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
    
class ViewDeletedProducts(APIView):
  def get(self, request):
    if not request.user.is_staff:
      return Response(
        {'error': 'Unauthorized to perform this action'},
        status=status.HTTP_401_UNAUTHORIZED
        )
    products = Product.objects.filter(is_deleted=True)
    serializer = ProductSerializer(products, many=True)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
      )
      
      
class CategoryProductShop_productView(APIView):
  def get(self, request, category_id):
    try:
      category = Category.objects.get(id=category_id)
    except Category.DoesNotExist:
      return Response(
        {'error': 'Category not found'},
        status=status.HTTP_404_NOT_FOUND
        )
    products = category.products.filter(is_deleted=False)
    serializer = ProductSerializer(products, many=True)
    shop_products = category.shop_products.filter(is_available=True)
    shop_productserializer = Shop_productSerializer(shop_products, many=True)
    return Response(
      {'products': serializer.data,
        'shop_products': shop_productserializer.data
      },
      status=status.HTTP_200_OK
      )
      
      
class ProductReviewView(APIView):
  def get(self, request, product_id=None, shop_product_id=None):
    
    if product_id:
      reviews = ProductReview.objects.filter(product__id=product_id, is_deleted=False)
    elif shop_product_id:
      reviews = ProductReview.objects.filter(shop_product__id=shop_product_id, is_deleted=False)
    else:
      return Response(
        {'error': 'No product specified'}, status=status.HTTP_400_BAD_REQUEST
      )
    serializer = ProductReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
  def post(self, request, product_id=None, shop_product_id=None):
    if not request.user.is_authenticated:
      return Response({'error': 'Login to leave reviews on products'}, status=status.HTTP_400_BAD_REQUEST)
    product = None
    shop_product = None
    
    if product_id:
      try:
        product = Product.objects.get(id=product_id)
      except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
      has_bought = Order.objects.filter(buyer=request.user, items__product=product).exists()
      if not has_bought:
        return Response({'error': 'You must purchase this product before reviewing'}, status=status.HTTP_400_BAD_REQUEST)
      review_count = ProductReview.objects.filter(product=product, buyer=request.user).count()
      if review_count >= 3:
        return Response({'error': 'You can only review a product three times'}, status=status.HTTP_400_BAD_REQUEST)
    elif shop_product_id:
      try:
        shop_product = Shop_product.objects.get(id=shop_product_id)
      except Shop_product.DoesNotExist:
        return Response(
          {'error': 'Product not found'},
          status=status.HTTP_404_NOT_FOUND
        )
      has_bought = Order.objects.filter(buyer=request.data, items__shop_product=shop_product).exists()
      if not has_bought:
        return Response({'error': 'You must purchase this product before reviewing'}, status=status.HTTP_400_BAD_REQUEST)
      review_count = ProductReview.objects.filter(shop_product=shop_product, buyer=request.user).count()
      if review_count >= 3:
        return Response({'error': 'You can only review a product three times'}, status=status.HTTP_400_BAD_REQUEST)
    serializer = ProductReviewSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(buyer=request.user, product=product, shop_product=shop_product)
      return Response(
        serializer.data,
        status=status.HTTP_200_OK
      )
    return Response(
      serializers.errors,
      status=status.HTTP_400_BAD_REQUEST
    )
    
    
class ProductReviewDetailView(APIView):
  def get(self, request, review_id):
    try:
      review = ProductReview.objects.get(id=review_id, is_deleted=False)
    except ProductReview.DoesNotExist:
      return Response(
        {'error': 'Review not found'},
        status=status.HTTP_404_NOT_FOUND
      )
    serializer = ProductReviewSerializer(review)
    return Response(
      serializer.data,
      status=status.HTTP_200_OK
    )
    
  def put(self, request, review_id):
    try:
      review = ProductReview.objects.get(id=review_id, is_deleted=False)
    except ProductReview.DoesNotExist:
      return Response(
        {'Review not foud'},
        status=status.HTTP_404_NOT_FOUND
      )
    if review.buyer != request.user:
      return Response(
        {'error': 'Not your review'},
        status=status.HTTP_403_FORBIDDEN
      )
    review.is_deleted = True
    review.save()
    return Response(
      {'message': 'Review deleted successfully'},
      status=status.HTTP_200_OK
    )
      