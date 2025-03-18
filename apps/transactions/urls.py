from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.transactions.views import (
    AddToCartView, CartView, RemoveFromCartView, UpdateCartItemTypeView, 
    CheckoutCartView, UpdateCartItemSharedUsersView, 
    RemoveSharedUserFromCartItemView, SharedRentalDetailsView
)

urlpatterns = [
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', CartView.as_view(), name='cart_view'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/update-type/<int:item_id>/', UpdateCartItemTypeView.as_view(), name='update_cart_item_type'),
    path('cart/checkout/', CheckoutCartView.as_view(), name='checkout_cart'),
    path('cart/update-shared-users/<int:item_id>/', UpdateCartItemSharedUsersView.as_view(), name='update_shared_users'),
    path('cart/remove-shared-user/<int:item_id>/<int:user_id>/', RemoveSharedUserFromCartItemView.as_view(), name='remove_shared_user'),
    path('shared-rental-details/<int:pk>/', SharedRentalDetailsView.as_view(), name='shared_rental_details')
]
