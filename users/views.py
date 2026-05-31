from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import token
from .models import customer_profile
from .serializers import UserSerializer, Customer_profileSerializer, ChangePasswordSerializer


class CreateAccountView(APIView):
  def post(self, request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response({'message': 'Account created successfully'},
      status=status.HTTP_201_CREATED
      )
    return Response(serializer.errors,
    status=status.HTTP_400_BAD_REQUEST
    )


class LoginView(APIView):
  def post(self, request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(password=password, username=username)
    if user:
      token, _ = Token.objects.get_or_create(user=user)
      return Response({'token': token.key}, status=status.HTTP_200_OK
      )
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORISED
      )
      
      
class Customer_profileView(APIView):
  permission_classess = [IsAuthenticated]
  
  def post(self, request):
    serializer = Customer_profileSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save(user=request.user)
      return Response(serializer.data,
      status=status.HTTP_201_CREATED
      )
    return Response(serializer.errors,
    status=status.HTTP_400_BAD_REQUEST
    )
    
  def get(self, request):
    profile = customer_profile.objects.get(user=request.user)
    serializer = Customer_profileSerializer(profile)
    return Response(serializer.data)
    
  def put(self, request):
    profile = customer_profile(user=request.user)
    serializer = Customer_profileSerializer(profile, data=request.data)
    if serializer.is_valid():
      serializer.save()
      return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
  def delete(self, request):
    profile = customer_profile(user=request.user)
    profile.delete()
    return Response({'message': 'Profile deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    
class ChangePasswordView(APIView):
  permission_classess = [IsAuthenticated]
  
  def put(self, request):
    user = request.user
    serializer = ChangePasswordSerializer(user, data=request.data context={'request': request})
    
    if serializer.is_valid():
      serializer.save()
      return Response({'message': 'Password changed successfully'},
      status=status.HTTP_200_OK
      )
    return Response(serializer.errors,
    status=status.HTTP_400_BAD_REQUEST
    )