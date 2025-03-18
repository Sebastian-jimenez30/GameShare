from .models import Game, Category, GameCategory, Recommendation, Review
from .interfaces import (
    IGameRepository,
    ICategoryRepository,
    IGameCategoryRepository,
    IRecommendationRepository,
    IReviewRepository
)
from django.db.models import Avg
from typing import List


class GameRepository(IGameRepository):
    def create_game(self, game_data: dict) -> Game:
        return Game.objects.create(**game_data)

    def get_game_by_id(self, game_id: int) -> Game:
        try:
            return Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return None

    def update_game(self, game_id: int, game_data: dict) -> Game:
        game = self.get_game_by_id(game_id)
        if game:
            for key, value in game_data.items():
                setattr(game, key, value)
            game.save()
        return game

    def delete_game(self, game_id: int) -> bool:
        game = self.get_game_by_id(game_id)
        if game:
            game.delete()
            return True
        return False

    def list_games(self) -> List[Game]:
        return list(Game.objects.all())


class CategoryRepository(ICategoryRepository):
    def create_category(self, category_data: dict) -> Category:
        return Category.objects.create(**category_data)

    def get_category_by_id(self, category_id: int) -> Category:
        try:
            return Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return None

    def list_categories(self) -> List[Category]:
        return list(Category.objects.all())


class GameCategoryRepository(IGameCategoryRepository):
    def assign_category_to_game(self, game_id: int, category_id: int):
        game = Game.objects.get(id=game_id)
        category = Category.objects.get(id=category_id)
        GameCategory.objects.create(game=game, category=category)

    def remove_category_from_game(self, game_id: int, category_id: int):
        GameCategory.objects.filter(game_id=game_id, category_id=category_id).delete()

    def get_categories_by_game(self, game_id: int) -> List[Category]:
        return list(Category.objects.filter(gamecategory__game_id=game_id))


class RecommendationRepository(IRecommendationRepository):
    def create_recommendation(self, user_id: int, game_id: int) -> Recommendation:
        return Recommendation.objects.create(user_id=user_id, game_id=game_id)

    def get_recommendations_by_user(self, user_id: int) -> List[Recommendation]:
        return list(Recommendation.objects.filter(user_id=user_id))


class ReviewRepository(IReviewRepository):
    def create_review(self, review_data: dict) -> Review:
        return Review.objects.create(**review_data)

    def get_reviews_by_game(self, game_id: int) -> List[Review]:
        return list(Review.objects.filter(game_id=game_id).order_by('-date'))

    def get_average_rating(self, game_id: int) -> float:
        average = Review.objects.filter(game_id=game_id).aggregate(Avg('rating'))['rating__avg']
        return round(average, 2) if average else 0.0
