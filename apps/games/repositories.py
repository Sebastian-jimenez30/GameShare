from typing import List, Optional
from django.db.models import Avg
from django.db.models import Count
from apps.users.models import User

from .models import (
    Game,
    Category,
    GameCategory,
    Recommendation,
    Review,
    GameRequirements
)
from .interfaces import (
    IGameRepository,
    ICategoryRepository,
    IGameCategoryRepository,
    IRecommendationRepository,
    IReviewRepository,
    IGameRequirementsRepository,
    IGameAnalyticsRepository
)


class GameRepository(IGameRepository):
    def create_game(self, game_data: dict) -> Game:
        game = Game.objects.create(**game_data)
        return game

    def get_game_by_id(self, game_id: int) -> Optional[Game]:
        return Game.objects.select_related("requirements").filter(id=game_id).first()

    def update_game(self, game_id: int, game_data: dict) -> Optional[Game]:
        game = self.get_game_by_id(game_id)
        if not game:
            return None

        requirements_data = game_data.pop("requirements", None)
        if requirements_data:
            for key, value in requirements_data.items():
                setattr(game.requirements, key, value)
            game.requirements.save()

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

    def list_games(self, only_available: bool = True) -> List[Game]:
        qs = Game.objects.select_related("requirements").all()
        if only_available:
            qs = qs.filter(available=True)
        return list(qs)


class CategoryRepository(ICategoryRepository):
    def create_category(self, category_data: dict) -> Category:
        return Category.objects.create(**category_data)

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        return Category.objects.filter(id=category_id).first()

    def list_categories(self) -> List[Category]:
        return list(Category.objects.all())


class GameCategoryRepository(IGameCategoryRepository):
    def assign_category_to_game(self, game_id: int, category_id: int) -> bool:
        try:
            game = Game.objects.get(id=game_id)
            category = Category.objects.get(id=category_id)
            GameCategory.objects.get_or_create(game=game, category=category)
            return True
        except (Game.DoesNotExist, Category.DoesNotExist):
            return False

    def remove_category_from_game(self, game_id: int, category_id: int) -> None:
        GameCategory.objects.filter(game_id=game_id, category_id=category_id).delete()

    def get_categories_by_game(self, game_id: int) -> List[Category]:
        return list(Category.objects.filter(gamecategory__game_id=game_id))


class RecommendationRepository(IRecommendationRepository):
    def create_recommendation(self, user_id: int, game_id: int, reason: str) -> Recommendation:
        return Recommendation.objects.create(user_id=user_id, game_id=game_id, reason=reason)

    def get_recommendations_by_user(self, user_id: int) -> List[Recommendation]:
        return list(Recommendation.objects.filter(user_id=user_id))

    def get_user_by_id(self, user_id: int) -> User:
        return User.objects.get(id=user_id)

    def get_all_games(self) -> List[Game]:
        return list(Game.objects.select_related('requirements').all())

    def clear_recommendations_for_user(self, user_id: int) -> None:
        Recommendation.objects.filter(user_id=user_id).delete()



class ReviewRepository(IReviewRepository):
    def create_review(self, review_data: dict) -> Review:
        return Review.objects.create(**review_data)

    def get_reviews_by_game(self, game_id: int) -> List[Review]:
        return list(Review.objects.filter(game_id=game_id).order_by('-date'))

    def get_average_rating(self, game_id: int) -> float:
        avg_rating = Review.objects.filter(game_id=game_id).aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating or 0.0, 2)

class GameRequirementsRepository(IGameRequirementsRepository):
    def create_requirements(self, requirements_data: dict) -> GameRequirements:
        return GameRequirements.objects.create(**requirements_data)

    def update_requirements(self, requirements_id: int, data: dict) -> Optional[GameRequirements]:
        reqs = GameRequirements.objects.filter(id=requirements_id).first()
        if reqs:
            for key, value in data.items():
                setattr(reqs, key, value)
            reqs.save()
        return reqs

    def delete_requirements(self, requirements_id: int) -> bool:
        deleted, _ = GameRequirements.objects.filter(id=requirements_id).delete()
        return deleted > 0

    def get_by_id(self, requirements_id: int) -> Optional[GameRequirements]:
        return GameRequirements.objects.filter(id=requirements_id).first()

class GameAnalyticsRepository(IGameAnalyticsRepository): 
    def get_top_purchased_games(self, limit: int = 10) -> List[Game]:
        return (
            Game.objects.filter(transactions__transaction_type='purchase')
            .annotate(purchase_count=Count('transactions'))
            .order_by('-purchase_count')[:limit]
        )

    def get_top_rented_games(self, limit: int = 10) -> List[Game]:
        return (
            Game.objects.filter(
                transactions__transaction_type__in=['rental', 'shared_rental']
            )
            .annotate(rental_count=Count('transactions'))
            .order_by('-rental_count')[:limit]
        )