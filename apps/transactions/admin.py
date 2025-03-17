from django.contrib import admin

from django.contrib import admin
from .models import (
    Rental,
    Purchase,
    SharedRental,
    SharedRentalPayment,
    Cart,
    Invoice,
    Payment
)


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'game', 'status', 'start_date', 'end_date', 'total_price')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('user__username', 'game__title')


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'game', 'date')
    list_filter = ('date',)
    search_fields = ('user__username', 'game__title')


@admin.register(SharedRental)
class SharedRentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'game', 'get_users')

    def get_users(self, obj):
        return ", ".join([user.username for user in obj.users.all()])
    get_users.short_description = 'Users'


@admin.register(SharedRentalPayment)
class SharedRentalPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'shared_rental', 'user', 'amount', 'status', 'payment_date')
    list_filter = ('status', 'payment_date')
    search_fields = ('user__username', 'shared_rental__game__title')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'date', 'purchase_transaction', 'rental_transaction')
    list_filter = ('date',)
    search_fields = ('user__username',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'method', 'status', 'date')
    list_filter = ('method', 'status', 'date')
    search_fields = ('user__username',)

