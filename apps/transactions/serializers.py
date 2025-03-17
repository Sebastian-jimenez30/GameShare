from rest_framework import serializers
from apps.users.models import User
from .models import (
    Rental,
    Purchase,
    SharedRental,
    SharedRentalPayment,
    Cart,
    CartItem,
    Invoice,
    Payment
)


class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = '__all__'


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = '__all__'


class SharedRentalSerializer(serializers.ModelSerializer):
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)

    class Meta:
        model = SharedRental
        fields = ['id', 'game', 'users']


class SharedRentalPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SharedRentalPayment
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'game', 'item_type', 'quantity']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(source='cartitem_set', many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'total', 'items']
        read_only_fields = ['user', 'total']

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
