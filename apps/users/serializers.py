from rest_framework import serializers
from .models import User, Customer, AdminProfile


class CustomerNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        exclude = ['user', 'loyalty_points']


class UserSerializer(serializers.ModelSerializer):
    customer = CustomerNestedSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'password', 'customer']
        extra_kwargs = {'password': {'write_only': True}, 'email': {'required': True}}

    def create(self, validated_data):
        customer_data = validated_data.pop('customer', None)
        user = User.objects.create_user(**validated_data)

        if user.user_type == 'customer' and customer_data:
            customer_data.pop('loyalty_points', None)
            Customer.objects.create(
                    user=user,
                    loyalty_points=0,
                    **customer_data
            )

        return user


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = '__all__'
