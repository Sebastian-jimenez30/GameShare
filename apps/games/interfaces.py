from abc import ABC, abstractmethod
from typing import List, Optional
from .models import Game, Category, Recommendation, Review, GameRequirements


class IGameRepository(ABC):
    @abstractmethod
    def create_game(self, game_data: dict) -> Game:
        pass

    @abstractmethod
    def get_game_by_id(self, game_id: int) -> Optional[Game]:
        pass

    @abstractmethod
    def update_game(self, game_id: int, game_data: dict) -> Optional[Game]:
        pass

    @abstractmethod
    def delete_game(self, game_id: int) -> bool:
        pass

    @abstractmethod
    def list_games(self, only_available: bool = True) -> List[Game]:
        pass


class ICategoryRepository(ABC):
    @abstractmethod
    def create_category(self, category_data: dict) -> Category:
        pass

    @abstractmethod
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        pass

    @abstractmethod
    def list_categories(self) -> List[Category]:
        pass


class IGameCategoryRepository(ABC):
    @abstractmethod
    def assign_category_to_game(self, game_id: int, category_id: int) -> bool:
        pass

    @abstractmethod
    def remove_category_from_game(self, game_id: int, category_id: int) -> None:
        pass

    @abstractmethod
    def get_categories_by_game(self, game_id: int) -> List[Category]:
        pass


class IRecommendationRepository(ABC):
    @abstractmethod
    def create_recommendation(self, user_id: int, game_id: int, reason: str) -> Recommendation:
        pass

    @abstractmethod
    def get_recommendations_by_user(self, user_id: int) -> List[Recommendation]:
        pass


class IReviewRepository(ABC):
    @abstractmethod
    def create_review(self, review_data: dict) -> Review:
        pass

    @abstractmethod
    def get_reviews_by_game(self, game_id: int) -> List[Review]:
        pass

    @abstractmethod
    def get_average_rating(self, game_id: int) -> float:
        pass


class IGameRequirementsRepository(ABC): 

    @abstractmethod
    def create_requirements(self, requirements_data: dict) -> GameRequirements:
        pass

    @abstractmethod
    def get_by_id(self, requirements_id: int) -> Optional[GameRequirements]:
        pass

    @abstractmethod
    def update_requirements(self, requirements_id: int, data: dict) -> Optional[GameRequirements]:
        pass

    @abstractmethod
    def delete_requirements(self, requirements_id: int) -> bool:
        pass

class IGameAnalyticsRepository(ABC):
    @abstractmethod
    def get_top_purchased_games(self, limit: int = 10) -> List[Game]:
        pass

    @abstractmethod
    def get_top_rented_games(self, limit: int = 10) -> List[Game]:
        pass