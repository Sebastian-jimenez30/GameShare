from rest_framework import serializers
from .models import User, Customer, AdminProfile

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'password', 'user_type', 'customer']
        extra_kwargs = {'password': {'write_only': True}, 'email': {'required': True}}
