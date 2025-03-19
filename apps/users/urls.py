from django.urls import path
from . import views
from .views import UserRegistrationView, UserLoginView, UserLibraryView

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('register-form/', UserRegistrationView.as_view(), name='user_register_form'),
    path('login/', UserLoginView.as_view(), name='user_login_form'),
    path('library/', UserLibraryView.as_view(), name='user_library'),
]
