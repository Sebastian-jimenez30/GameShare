from typing import Any, Dict
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpRequest
from django.urls import reverse_lazy
from django.views.generic import TemplateView, View, FormView

from .forms import UserRegisterForm, UserLoginForm
from .services import UserService, UserLibraryService, UserSearchService
from .repositories import (
    UserRepository, 
    CustomerRepository, 
    AdminRepository, 
    UserLibraryRepository, 
    UserSearchRepository
)

user_service = UserService(UserRepository(), CustomerRepository(), AdminRepository())
library_service = UserLibraryService(UserLibraryRepository())
user_search_service = UserSearchService(UserSearchRepository())


class UserRegistrationView(FormView):
    template_name = "users/register_form.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy('user_login_form')

    def form_valid(self, form: UserRegisterForm):
        user_data = form.get_user_data()  
        user_service.create_user(user_data)  
        messages.success(self.request, "Usuario registrado exitosamente.")
        return super().form_valid(form)


class UserLoginView(FormView):
    template_name = 'users/login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('catalog')

    def form_valid(self, form: UserLoginForm):
        user = user_service.login_user(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password']
        )

        if user:
            login(self.request, user)
            messages.success(self.request, f"Bienvenido, {user.username}!")
            return super().form_valid(form)
        else:
            messages.error(self.request, "Credenciales inválidas.")
            return self.form_invalid(form)


class UserLibraryView(LoginRequiredMixin, TemplateView):
    template_name = 'users/library.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.update(
            library_service.get_user_library(self.request.user)
        )
        return context


class UserSearchView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args, **kwargs) -> JsonResponse:
        query = request.GET.get('q', '')
        users = user_search_service.search_users(query, request.user.id)
        results = [{'username': user.username, 'email': user.email} for user in users]
        return JsonResponse(results, safe=False)


class UserListView(LoginRequiredMixin, TemplateView):
    template_name = 'users/user_list.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['users'] = user_service.list_all_users()
        return context
