from django.urls import path
from . import views

urlpattern = [
  path('user', user.views)
  ]