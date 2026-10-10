from django.urls import path
from .views import (
  EventListCreateView,
  EventDetailView,
  EventItemListCreateView,
  EventItemDetailView,
  ActiveSalesView,
)


urlpatterns = [
  path('event/', EventListCreateView.as_view()),
  path('event/<int:pk>/', EventDetailView.as_view()),
  path('event/<int:event_id>/items/', EventItemListCreateView.as_view()),
  path('event-item/<int:pk>/', EventItemDetailView.as_view()),
  path('active-sales/', ActiveSalesView.as_view()),
]