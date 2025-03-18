from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.http import JsonResponse
from .models import User, Customer, AdminProfile
from .serializers import UserSerializer, CustomerSerializer, AdminProfileSerializer
from .forms import UserRegisterForm, UserLoginForm
from .services import UserService, UserLibraryService, UserSearchService
from .repositories import UserRepository, CustomerRepository, AdminRepository, UserLibraryRepository, UserSearchRepository
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View


user_repo = UserRepository()
customer_repo = CustomerRepository()
admin_repo = AdminRepository()
user_service = UserService(user_repo, customer_repo, admin_repo)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class AdminProfileViewSet(viewsets.ModelViewSet):
    queryset = AdminProfile.objects.all()
    serializer_class = AdminProfileSerializer

class UserRegistrationView(FormView):
    template_name = "users/register_form.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy('user_login_form')

    def form_valid(self, form):
        user_data = form.get_user_data()  
        user_service.create_user(user_data)  
        return super().form_valid(form)

class UserLoginView(FormView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('catalog')

    def form_valid(self, form):
        user = user_service.login_user( 
            form.cleaned_data['username'],
            form.cleaned_data['password']
        )

        if user:
            login(self.request, user)
            return super().form_valid(form)
        else:
            messages.error(self.request, "Credenciales inválidas.")
            return self.form_invalid(form)
 
library_repo = UserLibraryRepository()
library_service = UserLibraryService(library_repo)

class UserLibraryView(LoginRequiredMixin, TemplateView):
    template_name = 'users/library.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(library_service.get_user_library(self.request.user))
        return context

class UserSearchView(LoginRequiredMixin, View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_search_service = UserSearchService(UserSearchRepository())

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        users = self.user_search_service.search_users(query, request.user.id)
        results = [{'username': user.username} for user in users]
        return JsonResponse(results, safe=False)
