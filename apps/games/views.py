from rest_framework import viewsets
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Game, Category, GameCategory, Recommendation, Review
from .serializers import GameSerializer, CategorySerializer, GameCategorySerializer, RecommendationSerializer, ReviewSerializer

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

