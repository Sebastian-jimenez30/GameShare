from django.shortcuts import render, redirect
from django.views.generic import TemplateView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import GameForm, ReviewForm
from .services import GameService, ReviewService  
from .repositories import GameRepository, ReviewRepository, GameCategoryRepository

game_service = GameService(GameRepository(), GameCategoryRepository())
review_service = ReviewService(ReviewRepository())


class CatalogView(LoginRequiredMixin, TemplateView):
    template_name = 'games/catalog.html'
    login_url = 'user_login_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['games'] = game_service.list_games()  
        return context


class GameDetailView(DetailView):
    template_name = 'games/game_detail.html'
    context_object_name = 'game'

    def get_object(self):
        game_id = self.kwargs.get("pk")
        return game_service.get_game_by_id(game_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.get_object()
        context['reviews'] = review_service.get_reviews_for_game(game.id)
        context['review_form'] = ReviewForm()
        context['categories'] = game.category.all()
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

        return render(request, self.template_name, {'game': game, 'review_form': form})


class GameCreateView(UserPassesTestMixin, CreateView):
    form_class = GameForm
    template_name = 'games/game_form.html'
    success_url = reverse_lazy('catalog')

    def test_func(self):
        return self.request.user.is_superuser  

    def form_valid(self, form):
        game_data = form.cleaned_data
        categories = game_data.pop('categories', [])
        game = game_service.create_game(game_data, [cat.id for cat in categories])
        return redirect('catalog')

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
        game_data = form.cleaned_data
        categories = game_data.pop('categories', None)  # Obtenemos las categorías seleccionadas

        category_ids = [cat.id for cat in categories] if categories else []

        # Actualizamos los datos del juego, pero solo si hay cambios en las categorías
        game_service.update_game(game.id, game_data, category_ids)

        return redirect(self.success_url)




class GameDeleteView(UserPassesTestMixin, DeleteView):
    template_name = 'games/game_confirm_delete.html'
    success_url = reverse_lazy('catalog')

    def test_func(self):
        return self.request.user.is_superuser  
    def get_object(self):
        return game_service.get_game_by_id(self.kwargs.get("pk"))

    def post(self, request, *args, **kwargs):
        game_service.delete_game(self.get_object().id)
        return redirect(self.success_url)
