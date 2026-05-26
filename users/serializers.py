from rest_framework import serializers
from .models import user, customer_profile

class UserSerializer(serializers.ModelSerializer):
  
  password = serializers.CharField(write_only=True)
  
  class Meta:
    model = user
    fields = [
      'id',
      'username',
      'email',
      'password',
      ]
      
    read_only_fields = ['id']
    
  def create(self, validated_data):
    user_instance = user.object.create_user(**validated_data)
    return user_instance
    
    
class Customer_profileSerializer(serializers.ModelSerializer):
  
  class Meta:
    model = customer_profile
    fields = '__all__'
    read_only_fields = ['user']
  