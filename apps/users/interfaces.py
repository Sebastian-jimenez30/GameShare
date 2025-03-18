from abc import ABC, abstractmethod
from .models import User
from apps.games.models import Game
from typing import List

class IUserRepository(ABC):
    @abstractmethod
    def create_user(self, user_data: dict):
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int):
        pass

    @abstractmethod
    def authenticate_user(self, username: str, password: str):
        pass

class ICustomerRepository(ABC):
    @abstractmethod
    def create_customer(self, user: User, customer_data: dict):
        pass

class IAdminRepository(ABC):
    @abstractmethod
    def create_admin(self, user: User):
        pass


class IUserLibraryRepository(ABC):
    @abstractmethod
    def get_purchased_games(self, user) -> List[Game]:
        pass

    @abstractmethod
    def get_rented_games(self, user) -> List[Game]:
        pass

    @abstractmethod
    def get_shared_rentals(self, user) -> dict:
        pass

class IUserSearchRepository(ABC):
    @abstractmethod
    def search_users(self, query: str, exclude_user_id: int) -> List[User]:
        pass