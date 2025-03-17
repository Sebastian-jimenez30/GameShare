from rest_framework import viewsets
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Game, Category, GameCategory, Recommendation, Review
from .serializers import GameSerializer, CategorySerializer, GameCategorySerializer, RecommendationSerializer, ReviewSerializer
from django.views.generic import DetailView
from .forms import ReviewForm, GameForm
from django.views.generic import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin

class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class GameCategoryViewSet(viewsets.ModelViewSet):
    queryset = GameCategory.objects.all()
    serializer_class = GameCategorySerializer

class RecommendationViewSet(viewsets.ModelViewSet):
    queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

import requests
from django.views.generic import TemplateView

class CatalogView(LoginRequiredMixin, TemplateView):
    template_name = 'games/catalog.html'
    login_url = 'user_login_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['games'] = Game.objects.all()
        return context
    
class GameDetailView(DetailView):
    model = Game
    template_name = 'games/game_detail.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.filter(game=self.object).order_by('-date')
        context['review_form'] = ReviewForm()  # Agrega el formulario de reseña al contexto
        context['categories'] = self.object.category.all()  # Obtiene todas las categorías asociadas al juego
        return context

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.game = game
            review.user = request.user  # Asigna el usuario actual
            review.save()
            return redirect('game_detail', pk=game.pk)  # Redirige al detalle del juego para ver la nueva reseña
        return render(request, self.template_name, {'game': game, 'review_form': form})
class GameCreateView(UserPassesTestMixin, CreateView):
    model = Game
    form_class = GameForm
    template_name = 'games/game_form.html'
    success_url = reverse_lazy('catalog')

    def test_func(self):
        return self.request.user.is_superuser  # Solo superusuarios pueden acceder a esta vista

    def form_valid(self, form):
        # Asigna el usuario actual al juego
        form.instance.user = self.request.user  
        
        # Guardamos el juego primero
        game = form.save()

        # Obtenemos las categorías seleccionadas desde el formulario
        categories = form.cleaned_data.get('categories')

        # Creamos las relaciones en la tabla intermedia GameCategory
        for category in categories:
            GameCategory.objects.create(game=game, category=category)

        return super().form_valid(form)


class GameEditView(UserPassesTestMixin, UpdateView):
    model = Game
    form_class = GameForm
    template_name = 'games/game_form.html'
    success_url = reverse_lazy('catalog')

    def test_func(self):
        return self.request.user.is_superuser  # Solo superusuarios pueden acceder a esta vista

    def form_valid(self, form):
        # Asigna el usuario actual al juego
        form.instance.user = self.request.user
        
        # Guardamos el juego primero
        game = form.save()

        # Eliminamos las relaciones previas en GameCategory para este juego
        GameCategory.objects.filter(game=game).delete()

        # Obtenemos las categorías seleccionadas desde el formulario
        categories = form.cleaned_data.get('categories')

        # Creamos las nuevas relaciones en la tabla intermedia GameCategory
        for category in categories:
            GameCategory.objects.create(game=game, category=category)

        return super().form_valid(form)

class GameDeleteView(UserPassesTestMixin, DeleteView):
    model = Game
    template_name = 'games/game_confirm_delete.html'
    success_url = reverse_lazy('catalog')

    def test_func(self):
        return self.request.user.is_superuser  # Solo superusuarios pueden acceder a esta vista