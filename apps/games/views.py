from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import GameForm, ReviewForm
from .services import GameService, ReviewService, CatalogService, RecommendationService, LocationService, CryptoService
from .repositories import GameRepository, ReviewRepository, GameCategoryRepository, GameRequirementsRepository, GameAnalyticsRepository, RecommendationRepository
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Game
from .serializers import GameSerializer

# Servicios
game_service = GameService(GameRepository(), GameCategoryRepository(), GameRequirementsRepository())
review_service = ReviewService(ReviewRepository())
catalog_service = CatalogService(GameAnalyticsRepository()) 


class CatalogView(LoginRequiredMixin, TemplateView):
    """
    Muestra el catálogo dividido en secciones: top rentas, top compras y todos los juegos.
    """
    template_name = 'games/catalog.html'
    login_url = 'user_login_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        catalog_data = catalog_service.get_catalog_sections()
        context.update(catalog_data)
        context.update(LocationService.get_user_location())
        return context


class GameDetailView(DetailView):
    """
    Muestra el detalle de un juego, sus categorías y reseñas.
    Permite enviar una reseña desde POST.
    """
    template_name = 'games/game_detail.html'
    context_object_name = 'game'

    def get_object(self):
        return game_service.get_game_by_id(self.kwargs.get("pk"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.get_object()
        
        crypto_prices = CryptoService.convert_usd_to_crypto(float(game.purchase_price))
    
        context.update({
            'reviews': review_service.get_reviews_for_game(game.id),
            'review_form': ReviewForm(),
            'categories': game.categories.all(),
            'btc_price': crypto_prices['btc'],
            'eth_price': crypto_prices['eth'],
        })
        return context

    def post(self, request, *args, **kwargs):
        game = self.get_object()
        form = ReviewForm(request.POST)

        if form.is_valid():
            review_data = {
                "user": request.user,
                "game": game,
                "rating": form.cleaned_data['rating'],
                "comment": form.cleaned_data['comment']
            }
            review_service.add_review(review_data)
            return redirect('game_detail', pk=game.id)

        return render(request, self.template_name, {
            'game': game,
            'review_form': form,
            'reviews': review_service.get_reviews_for_game(game.id),
            'categories': game.categories.all()
        })


class GameCreateView(UserPassesTestMixin, CreateView):
    form_class = GameForm
    template_name = 'games/game_form.html'
    success_url = reverse_lazy('catalog')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        game_data = {
            key: form.cleaned_data[key]
            for key in [
                'title', 'developer', 'release_year',
                'purchase_price', 'rental_price_per_hour',
                'rental_price_per_day', 'image', 'available'
            ]
        }

        category_ids = [cat.id for cat in form.cleaned_data.get('categories', [])]

        # Agrupamos todos los campos de requisitos en un solo dict
        requirements_data = {
            'min_processor': form.cleaned_data.get('min_cpu'),
            'min_ram_gb': int(form.cleaned_data.get('min_ram') or 0),
            'min_gpu': form.cleaned_data.get('min_gpu'),
            'rec_processor': form.cleaned_data.get('rec_cpu'),
            'rec_ram_gb': int(form.cleaned_data.get('rec_ram') or 0),
            'rec_gpu': form.cleaned_data.get('rec_gpu'),
        }

        game_service.create_game(
            game_data=game_data,
            category_ids=category_ids,
            requirements_data=requirements_data
        )
        return redirect(self.success_url)

class GameEditView(UserPassesTestMixin, UpdateView):
    form_class = GameForm
    template_name = 'games/game_form.html'
    success_url = reverse_lazy('catalog')

    def test_func(self):
        return self.request.user.is_superuser

    def get_object(self):
        return game_service.get_game_by_id(self.kwargs.get("pk"))

    def form_valid(self, form):
        game = self.get_object()

        game_data = {
            key: form.cleaned_data[key]
            for key in [
                'title', 'developer', 'release_year',
                'purchase_price', 'rental_price_per_hour',
                'rental_price_per_day', 'image', 'available'
            ]
        }

        category_ids = [cat.id for cat in form.cleaned_data.get('categories', [])]

        requirements_data = {
            'min_processor': form.cleaned_data.get('min_cpu'),
            'min_ram_gb': int(form.cleaned_data.get('min_ram') or 0),
            'min_gpu': form.cleaned_data.get('min_gpu'),
            'rec_processor': form.cleaned_data.get('rec_cpu'),
            'rec_ram_gb': int(form.cleaned_data.get('rec_ram') or 0),
            'rec_gpu': form.cleaned_data.get('rec_gpu'),
        }

        game_service.update_game(
            game_id=game.id,
            game_data=game_data,
            category_ids=category_ids,
            requirements_data=requirements_data
        )
        return redirect(self.success_url)



class GameDeleteView(UserPassesTestMixin, DeleteView):
    """
    Confirmación y eliminación de un juego. Solo accesible por admin.
    """
    template_name = 'games/game_confirm_delete.html'
    success_url = reverse_lazy('catalog')

    def test_func(self):
        return self.request.user.is_superuser

    def get_object(self):
        return game_service.get_game_by_id(self.kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        game_service.delete_game(self.get_object().id)
        return redirect(self.success_url)


class RecommendationListView(LoginRequiredMixin, TemplateView):
    template_name = 'games/recommendations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = RecommendationService(RecommendationRepository())

        # Generar (si no existen) y obtener recomendaciones para el usuario
        service.recommend_based_on_hardware(self.request.user)
        context['recommendations'] = service.get_user_recommendations(self.request.user.id)
        return context

class AvailableGamesAPIView(APIView):
    def get(self, request):
        games = Game.objects.filter(available=True)
        serializer = GameSerializer(games, many=True, context={'request': request})
        return Response(serializer.data)