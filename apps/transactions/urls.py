from django.urls import path
from apps.transactions.views import (
    AddToCartView, CartView, RemoveFromCartView, UpdateCartItemTypeView, 
    CheckoutCartView, UpdateCartItemSharedUsersView, 
    RemoveSharedUserFromCartItemView, SharedRentalDetailsView, CompleteSharedPaymentView, UpdateCartItemQuantityView,
    InvoiceDownloadView, BillingView, CompletePaymentView
)

urlpatterns = [
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/', CartView.as_view(), name='cart_view'),
    path('cart/remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/update-type/<int:item_id>/', UpdateCartItemTypeView.as_view(), name='update_cart_item_type'),
    path('cart/checkout/', CheckoutCartView.as_view(), name='checkout_cart'),

    path('cart/update-shared-users/<int:item_id>/', UpdateCartItemSharedUsersView.as_view(), name='update_shared_users'),
    path('cart/remove-shared-user/<int:item_id>/<int:user_id>/', RemoveSharedUserFromCartItemView.as_view(), name='remove_shared_user'),

    path('shared-rental-details/<int:pk>/', SharedRentalDetailsView.as_view(), name='shared_rental_details'),
    path('shared-payment/<int:payment_id>/complete/', CompleteSharedPaymentView.as_view(), name='complete_shared_payment'),
    path('cart/update-quantity/<int:item_id>/', UpdateCartItemQuantityView.as_view(), name='update_cart_item_quantity'),
    path('payments/invoice/<int:invoice_id>/', InvoiceDownloadView.as_view(), name='download_invoice'),
    path('cart/billing/', BillingView.as_view(), name='billing_summary'),
    path('cart/payment/', CompletePaymentView.as_view(), name='complete_payment'),

]
