from .interfaces import (
    IGameRepository,
    ICategoryRepository,
    IGameCategoryRepository,
    IRecommendationRepository,
    IReviewRepository
)
from typing import List
from .models import Game


class GameService:
    def __init__(self, game_repo: IGameRepository, game_category_repo: IGameCategoryRepository):
        self.game_repo = game_repo
        self.game_category_repo = game_category_repo

    def create_game(self, game_data: dict, category_ids: List[int]):
        game = self.game_repo.create_game(game_data)
        for category_id in category_ids:
            self.game_category_repo.assign_category_to_game(game.id, category_id)
        return game

    def update_game(self, game_id: int, game_data: dict, category_ids: List[int] = None) -> Game:
        game = self.game_repo.update_game(game_id, game_data)
        
        if game:
            # Solo actualizamos las categorías si 'category_ids' no está vacío
            if category_ids:
                # Eliminar las categorías anteriores y asignar las nuevas
                self.game_category_repo.remove_category_from_game(game_id, category_ids)
                for category_id in category_ids:
                    self.game_category_repo.assign_category_to_game(game_id, category_id)

        return game

    def delete_game(self, game_id: int) -> bool:
        return self.game_repo.delete_game(game_id)

    def list_games(self):
        return self.game_repo.list_games()

    def get_game_by_id(self, game_id: int):
        return self.game_repo.get_game_by_id(game_id)


class CategoryService:
    def __init__(self, category_repo: ICategoryRepository):
        self.category_repo = category_repo

    def create_category(self, category_data: dict):
        return self.category_repo.create_category(category_data)

    def list_categories(self):
        return self.category_repo.list_categories()


class RecommendationService:
    def __init__(self, recommendation_repo: IRecommendationRepository):
        self.recommendation_repo = recommendation_repo

    def recommend_game(self, user_id: int, game_id: int):
        return self.recommendation_repo.create_recommendation(user_id, game_id)

    def get_user_recommendations(self, user_id: int):
        return self.recommendation_repo.get_recommendations_by_user(user_id)


class ReviewService:
    def __init__(self, review_repo: IReviewRepository):
        self.review_repo = review_repo

    def add_review(self, review_data: dict):
        return self.review_repo.create_review(review_data)

    def get_reviews_for_game(self, game_id: int):
        return self.review_repo.get_reviews_by_game(game_id)

    def get_game_rating(self, game_id: int):
        return self.review_repo.get_average_rating(game_id)
