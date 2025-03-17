from rest_framework import serializers
from .models import User, Customer, AdminProfile
from apps.transactions.models import Purchase, Rental
from apps.games.models import Game


class CustomerNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        exclude = ['user', 'loyalty_points']


class UserSerializer(serializers.ModelSerializer):
    customer = CustomerNestedSerializer(required=False)
    purchased_games = serializers.SerializerMethodField()
    rented_games = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'password', 'customer','purchased_games','rented_games']
        extra_kwargs = {'password': {'write_only': True}, 'email': {'required': True}}

    def get_purchased_games(self, obj):
        purchases = Purchase.objects.filter(user=obj)
        return PurchaseSerializer(purchases, many=True).data

    def get_rented_games(self, obj):
        rentals = Rental.objects.filter(user=obj)
        return RentalSerializer(rentals, many=True).data

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

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ['id', 'title', 'developer', 'year', 'price']

class PurchaseSerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = Purchase
        fields = ['game']

class RentalSerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = Rental
        fields = ['game', 'start_date', 'end_date', 'status']
