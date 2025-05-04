from typing import Optional, List
from .interfaces import (
    IUserRepository,
    IUserLibraryRepository,
    IUserSearchRepository
)
from .models import User


class UserService:
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    def create_user(self, user_data: dict) -> User:
        """
        Crea un usuario con sus datos completos.
        """
        return self.user_repo.create_user(user_data)

    def login_user(self, username: str, password: str) -> Optional[User]:
        """
        Autentica un usuario por sus credenciales.
        """
        return self.user_repo.authenticate_user(username, password)


class UserLibraryService:
    def __init__(self, library_repo: IUserLibraryRepository):
        self.library_repo = library_repo

    def get_user_library(self, user: User) -> dict:
        """
        Obtiene todos los juegos del usuario: comprados, alquilados y rentas compartidas.
        """
        shared_rentals = self.library_repo.get_shared_rentals(user)
        return {
            "purchased_games": self.library_repo.get_purchased_games(user),
            "rented_games": self.library_repo.get_rented_games(user),
            "available_shared_rentals": shared_rentals["available"],
            "unavailable_shared_rentals": shared_rentals["unavailable"],
        }


class UserSearchService:
    def __init__(self, user_search_repo: IUserSearchRepository):
        self.user_search_repo = user_search_repo

    def search_users(self, query: str, exclude_user_id: int) -> List[User]:
        """
        Busca usuarios por nombre o username.
        """
        return self.user_search_repo.search_users(query, exclude_user_id)
