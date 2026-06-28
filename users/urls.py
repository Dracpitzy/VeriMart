from django.urls import path
from .views import CreateAccountView, LoginView, Customer_profileView, ChangePasswordView

urlpatterns = [
  path('create/', CreateAccountView.as_view() ),
  path('login/', LoginView.as_view()),
  path('profile/', Customer_profileView.as_view()),
  path('change-password/', ChangePasswordView.as_view())
  ]