from abc import ABC, abstractmethod
from typing import List, Optional
from .models import User
from apps.games.models import Game


class IUserRepository(ABC):
    """
    Define las operaciones relacionadas con usuarios.
    """

    @abstractmethod
    def create_user(self, user_data: dict) -> User:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        pass

    @abstractmethod
    def list_all_users(self) -> List[User]:
        pass


class IUserLibraryRepository(ABC):
    """
    Define las operaciones para obtener la biblioteca de juegos de un usuario.
    """

    @abstractmethod
    def get_purchased_games(self, user: User) -> List[Game]:
        pass

    @abstractmethod
    def get_rented_games(self, user: User) -> List[Game]:
        pass

    @abstractmethod
    def get_shared_rentals(self, user: User) -> dict:
        pass


class IUserSearchRepository(ABC):
    """
    Define una interfaz para buscar usuarios.
    """

    @abstractmethod
    def search_users(self, query: str, exclude_user_id: int) -> List[User]:
        pass
