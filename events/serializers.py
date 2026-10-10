from decimal import Decimal
from django.utils import timezone
from rest_framework import serializers
from .models import Event, EventItem


class EventItemSerializer(serializers.ModelSerializer):
  shop_name = serializers.CharField(source='event.shop.name', read_only=True)
  event_name = serializers.CharField(source='event.name', read_only=True)
  event_start_date = serializers.DateTimeField(source='event.start_date', read_only=True)
  event_end_date = serializers.DateTimeField(source='event.end_date', read_only=True)
  shop_product_name = serializers.CharField(source='shop_product.name', read_only=True)
  original_price = serializers.DecimalField(source='shop_product.price', max_digits=10, decimal_places=2, read_only=True)
  discounted_price = serializers.SerializerMethodField()
  
  class Meta:
    model = EventItem
    fields = [
      'id', 'event', 'event_name', 'event_start_date', 'event_end_date', 'shop_name', 'shop_product', 'shop_product_name', 'percent_off', 'original_price', 'discounted_price', 'created_at',
    ]
    read_only_fields = ['created_at']
    
  def get_discounted_price(self, obj):
    percent_off = obj.percent_off or obj.event.percent_off
    
    if percent_off is None:
      return obj.shop_product.price
      
    discount = obj.shop_product.price * (Decimal(percent_off) / Decimal('100'))
    return (obj.shop_product.price - discount).quantize(Decimal('0.01'))
    
  def validate(self, attrs):
    event = attrs.get('event') or getattr(self.instance, 'event', None)
    shop_product = attrs.get('shop_product') or getattr(self.instance, 'shop_product', None)
    
    if shop_product.shop != event.shop:
      raise serializers.ValidationError('This product does not belong to the shop running this event')
      
    now = timezone.now()
    conflict = EventItem.objects.filter(
      shop_product=shop_product,
      event__start_date__lte=now,
      event__end_date__gte=now,
    )
    
    if self.instance:
      conflict = conflict.exclude(pk=self.instance.pk)
    if conflict.exists():
      raise serializers.ValidationError('This product is already part of an active sale.')
      
    return attrs
    
    
class EventSerializer(serializers.ModelSerializer):
  
  shop_name = serializers.CharField(source='shop.name', read_only=True)
  items = EventItemSerializer(many=True, read_only=True)
  
  class Meta:
    model = Event
    fields = [
      'id', 'shop', 'shop_name', 'name',
      'start_date', 'end_date',
      'percent_off', 'flyer', 'items', 'created_at',
    ]
    read_only_fields = ['shop', 'created_at']
    
  def validate_start_date(self, value):
    if value < timezone.now():
      raise serializers.ValidationError('Start day can not be in the past.')
    return value
    
  def validate(self, attrs):
    start = attrs.get('start_date') or getattr(self.instance, 'start_date', None)
    end = attrs.get('end_date') or getattr(self.instance, 'end_date', None)
    
    if start and end and end <= start:
      raise serializers.ValidationError('End date must be after start date.')
    return attrs
    
    
class EventListSerializer(serializers.ModelSerializer):
  
  shop_name = serializers.CharField(source='shop.name', read_only=True)
  
  class Meta:
    model = Event
    fields = [
      'id', 'shop', 'shop_name', 'name', 'start_date', 'end_date', 'percent_off', 'flyer', 'created_at',
    ]
    read_only_fields = fields