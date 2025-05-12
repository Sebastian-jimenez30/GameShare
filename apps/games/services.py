from typing import List, Optional
from apps.users.models import User
import requests


from .interfaces import (
    IGameRepository,
    ICategoryRepository,
    IGameCategoryRepository,
    IRecommendationRepository,
    IReviewRepository,
    IGameRequirementsRepository,
    IGameAnalyticsRepository
)
from .models import Game, Category, Review


class GameService:
    def __init__(
        self,
        game_repo: IGameRepository,
        game_category_repo: IGameCategoryRepository,
        requirements_repo: IGameRequirementsRepository
    ):
        self.game_repo = game_repo
        self.game_category_repo = game_category_repo
        self.requirements_repo = requirements_repo

    def create_game(self, game_data: dict, category_ids: List[int], requirements_data: dict) -> Game:
        requirements_instance = self.requirements_repo.create_requirements(requirements_data)
        game_data["requirements"] = requirements_instance

        game = self.game_repo.create_game(game_data)

        for category_id in category_ids:
            self.game_category_repo.assign_category_to_game(game.id, category_id)

        return game

    def update_game(self, game_id: int, game_data: dict, category_ids: Optional[List[int]] = None, requirements_data: Optional[dict] = None) -> Optional[Game]:
        game = self.game_repo.get_game_by_id(game_id)
        if not game:
            return None

        # Actualizar requisitos si se proporcionan
        if requirements_data:
            if game.requirements:
                self.requirements_repo.update_requirements(game.requirements.id, requirements_data)
            else:
                new_reqs = self.requirements_repo.create_requirements(requirements_data)
                game_data["requirements"] = new_reqs

        # Actualizar juego
        updated_game = self.game_repo.update_game(game_id, game_data)

        # Actualizar categorías
        if category_ids is not None:
            existing_categories = self.game_category_repo.get_categories_by_game(game_id)
            for category in existing_categories:
                self.game_category_repo.remove_category_from_game(game_id, category.id)
            for category_id in category_ids:
                self.game_category_repo.assign_category_to_game(game_id, category_id)

        return updated_game


    def delete_game(self, game_id: int) -> bool:
        return self.game_repo.delete_game(game_id)

    def list_games(self, only_available: bool = True) -> List[Game]:
        return self.game_repo.list_games(only_available)

    def get_game_by_id(self, game_id: int) -> Optional[Game]:
        return self.game_repo.get_game_by_id(game_id)

class CategoryService:
    def __init__(self, category_repo: ICategoryRepository):
        self.category_repo = category_repo

    def create_category(self, category_data: dict) -> Category:
        return self.category_repo.create_category(category_data)

    def list_categories(self) -> List[Category]:
        return self.category_repo.list_categories()


class RecommendationService:
    def __init__(self, recommendation_repo: IRecommendationRepository):
        self.recommendation_repo = recommendation_repo

    def recommend_based_on_hardware(self, user: User):
        self.recommendation_repo.clear_recommendations_for_user(user.id)

        for game in Game.objects.select_related('requirements').all():
            req = game.requirements
            reason = ""

            if (
                user.processor and req.min_processor.lower() in user.processor.lower()
                and user.ram_gb and user.ram_gb >= req.min_ram_gb
                and user.graphics_card and req.min_gpu.lower() in user.graphics_card.lower()
            ):
                reason = "Your hardware meets the minimum requirements."

            if (
                req.rec_processor and req.rec_processor.lower() in user.processor.lower()
                and req.rec_ram_gb and user.ram_gb and user.ram_gb >= req.rec_ram_gb
                and req.rec_gpu and req.rec_gpu.lower() in user.graphics_card.lower()
            ):
                reason = "Your hardware meets the recommended requirements."

            if reason:
                self.recommendation_repo.create_recommendation(user.id, game.id, reason)

    def get_user_recommendations(self, user_id: int):
        return self.recommendation_repo.get_recommendations_by_user(user_id)


class ReviewService:
    def __init__(self, review_repo: IReviewRepository):
        self.review_repo = review_repo

    def add_review(self, review_data: dict) -> Review:
        return self.review_repo.create_review(review_data)

    def get_reviews_for_game(self, game_id: int) -> List[Review]:
        return self.review_repo.get_reviews_by_game(game_id)

    def get_game_rating(self, game_id: int) -> float:
        return self.review_repo.get_average_rating(game_id)


class CatalogService:
    def __init__(self, analytics_repo: IGameAnalyticsRepository):
        self.analytics_repo = analytics_repo

    def get_catalog_sections(self) -> dict:
        return {
            'top_rented_games': self.analytics_repo.get_top_rented_games(),
            'top_purchased_games': self.analytics_repo.get_top_purchased_games(),
            'all_games': Game.objects.filter(available=True)
        }
class LocationService:
    @staticmethod
    def get_user_location() -> dict:
        try:
            response = requests.get('https://ipapi.co/json/')
            if response.status_code == 200:
                data = response.json()
                return {
                    'city': data.get('city', 'tu ciudad'),
                    'country': data.get('country_name', 'tu país')
                }
        except:
            pass
        return {
            'city': 'tu ciuda',
            'country': 'tu país'
        }

class CryptoService:
    @staticmethod
    def convert_usd_to_crypto(usd_amount: float) -> dict:
        try:
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': 'bitcoin,ethereum',
                'vs_currencies': 'usd'
            }
            response = requests.get(url, params=params, timeout=5)
            data = response.json()

            btc_usd = data['bitcoin']['usd']
            eth_usd = data['ethereum']['usd']

            return {
                'btc': round(usd_amount / btc_usd, 6),
                'eth': round(usd_amount / eth_usd, 6),
            }
        except:
            return {
                'btc': None,
                'eth': None,
            }
