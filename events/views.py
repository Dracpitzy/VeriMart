from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Event, EventItem
from .serializers import EventSerializer, EventListSerializer, EventItemSerializer


class EventListCreateView(APIView):
  
  def get(self, request):
    now = timezone.now()
    events = Event.objects.select_related('shop')
    
    shop_id = request.query_params.get('shop_id')
    if shop_id:
      events = events.filter(shop_id=shop_id)
      
    event_status = request.query_params.get('status')
    if event_status == 'active':
      events = events.filter(start_date__lte=now, end_date__gte=now).order_by('end_date')
    elif event_status == 'upcoming':
      events = events.filter(
        start_date__gt=now
      ).order_by('start_date')
    elif event_status == 'past':
      events = events.filter(end_date__lt=now).order_by('-end_date')
    elif event_status is None:
      events = events.order_by('-start_date')
    else:
      return Response(
        {'error': 'Status must be one of: active, upcoming, past'},
        status=status.HTTP_400_BAD_REQUEST
      )
    
    serializer = EventListSerializer(events, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
  def post(self, request):
    if not request.user.is_authenticated:
      return Response({'error': 'Login required'}, status=status.HTTP_401_UNAUTHORIZED)
    if not hasattr(request.user, 'shop'):
      return Response({'error': 'You do not own a shop'}, status=status.HTTP_403_FORBIDDEN)
      
    serializer = EventSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(shop=request.user.shop)
      return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
      
class EventDetailView(APIView):
  
  def get(self, request, pk):
    event = get_object_or_404(Event, pk=pk)
    serializer = EventSerializer(event)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
  def patch(self, request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if event.shop.owner != request.user and not request.user.is_staff:
      return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    serializer = EventSerializer(event, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
  def delete(self, request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if event.shop.owner != request.user and not request.user.is_staff:
      return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
      
    event.delete()
    return Response({'message': 'Event deleted'}, status=status.HTTP_204_NO_CONTENT)
    
    
class EventItemListCreateView(APIView):
  
  def get(self, request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    serializer = EventItemSerializer(event.items.all(), many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
    
  def post(self, request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    
    if event.shop.owner != request.user and not request.user.is_staff:
      return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
      
    data = request.data.copy()
    data['event'] = event_id
    
    serializer = EventItemSerializer(data=data)
    if serializer.is_valid():
      serializer.save()
      return Response(
        serializer.date, status=status.HTTP_201_CREATED
      )
    return Response(
      serializer.errors, status=status.HTTP_400_BAD_REQUEST
    )
    
    
class EventItemDetailView(APIView):
  
  def patch(self, request, pk):
    item = get_object_or_404(EventItem, pk=pk)
    if item.event.shop.owner != request.user and not request.user.is_staff:
      return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
      
    serializer = EventItemSerializer(item, data=request.data, partial=True)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
  def delete(self, request, pk):
    
    item = get_object_or_404(EventItem, pk=pk)
    
    if item.event.shop.owner != request.user and not request.user.is_staff:
      return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
      
    item.delete()
    return Response({'message': 'Item removed from event'}, status=status.HTTP_204_NO_CONTENT)
    

class ActiveSalesView(APIView):
  
  def get(self, request):
    now = timezone.now()
    active_items = EventItem.objects.select_related(
      'event__shop', 'shop_product'
    ).filter(
      event__start_date__lte=now,
      event__end_date__gte=now,
    )
    
    serializer = EventItemSerializer(active_items, many=True)
    return Response(serializer.date, status=status.HTTP_200_OK)