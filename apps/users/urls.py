from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CustomerViewSet, AdminProfileViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'admins', AdminProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
