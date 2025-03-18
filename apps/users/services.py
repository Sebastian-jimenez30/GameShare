from typing import Optional, List, Dict
from .interfaces import (
    IUserRepository, 
    ICustomerRepository, 
    IAdminRepository, 
    IUserLibraryRepository, 
    IUserSearchRepository
)
from .models import User


class UserService:
    def __init__(
        self, 
        user_repo: IUserRepository, 
        customer_repo: ICustomerRepository, 
        admin_repo: IAdminRepository
    ):
        self.user_repo = user_repo
        self.customer_repo = customer_repo
        self.admin_repo = admin_repo

    def create_user(self, user_data: dict) -> User:
        customer_data = user_data.pop('customer', None)
        user = self.user_repo.create_user(user_data)

        if user.user_type == 'customer' and customer_data:
            customer = self.customer_repo.create_customer(user, customer_data)
            user.customer = customer
            user.save()
        
        elif user.user_type == 'admin':
            self.admin_repo.create_admin(user)

        return user

    def login_user(self, username: str, password: str) -> Optional[User]:
        return self.user_repo.authenticate_user(username, password)

    def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        return self.user_repo.update_user(user_id, user_data)

    def delete_user(self, user_id: int) -> bool:
        return self.user_repo.delete_user(user_id)

    def list_all_users(self) -> List[User]:
        return self.user_repo.list_users()


class UserLibraryService:
    def __init__(self, library_repo: IUserLibraryRepository):
        self.library_repo = library_repo

    def get_user_library(self, user: User):
        return {
            "purchased_games": self.library_repo.get_purchased_games(user),
            "rented_games": self.library_repo.get_rented_games(user),
            "available_shared_rentals": self.library_repo.get_shared_rentals(user)["available"],
            "unavailable_shared_rentals": self.library_repo.get_shared_rentals(user)["unavailable"],
        }

class UserSearchService:
    def __init__(self, user_search_repo: IUserSearchRepository):
        self.user_search_repo = user_search_repo

    def search_users(self, query: str, exclude_user_id: int) -> List[User]:
        return self.user_search_repo.search_users(query, exclude_user_id)
