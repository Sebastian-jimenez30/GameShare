from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RentalViewSet,
    PurchaseViewSet,
    SharedRentalViewSet,
    SharedRentalPaymentViewSet,
    CartViewSet,
    InvoiceViewSet,
    PaymentViewSet
)

router = DefaultRouter()
router.register(r'rentals', RentalViewSet)
router.register(r'purchases', PurchaseViewSet)
router.register(r'shared-rentals', SharedRentalViewSet)
router.register(r'shared-rental-payments', SharedRentalPaymentViewSet)
router.register(r'carts', CartViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
