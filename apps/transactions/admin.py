from django.contrib import admin
from .models import (
    Transaction,
    Rental,
    SharedRental,
    SharedRentalPayment,
    Cart,
    CartItem,
    Invoice,
    Payment
)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'game', 'transaction_type', 'total_price', 'date')
    list_filter = ('transaction_type', 'date')
    search_fields = ('user__username', 'game__title')


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'transaction', 'rental_type', 'start_time', 'end_time', 'status')
    list_filter = ('rental_type', 'status', 'start_time')
    search_fields = ('transaction__user__username', 'transaction__game__title')


@admin.register(SharedRental)
class SharedRentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'created_by', 'start_time', 'end_time', 'total_cost', 'is_fully_paid')
    list_filter = ('start_time', 'end_time')
    search_fields = ('created_by__username', 'game__title')


@admin.register(SharedRentalPayment)
class SharedRentalPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'shared_rental', 'user', 'amount', 'status', 'payment_date')
    list_filter = ('status', 'payment_date')
    search_fields = ('user__username', 'shared_rental__game__title')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'game', 'item_type', 'quantity', 'rental_type')
    list_filter = ('item_type', 'rental_type')
    search_fields = ('cart__user__username', 'game__title')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'transaction', 'total', 'date')
    list_filter = ('date',)
    search_fields = ('user__username', 'transaction__game__title')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'method', 'status', 'date')
    list_filter = ('method', 'status', 'date')
    search_fields = ('user__username',)
