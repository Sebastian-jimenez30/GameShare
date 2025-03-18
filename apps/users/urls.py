from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, UserLoginView, UserLibraryView


urlpatterns = [
    path('register-form/', UserRegistrationView.as_view(), name='user_register_form'),
    path('', UserLoginView.as_view(), name='user_login_form'),
    path('library/', UserLibraryView.as_view(), name='user_library'),
]
