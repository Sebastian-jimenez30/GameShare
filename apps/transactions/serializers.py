from rest_framework import serializers
from apps.users.models import User
from .models import (
    Rental,
    Purchase,
    SharedRental,
    SharedRentalPayment,
    Cart,
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


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
