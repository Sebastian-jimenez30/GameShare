from .interfaces import IUserLibraryRepository


class UserService:
    def __init__(self, user_repo, customer_repo, admin_repo):
        self.user_repo = user_repo
        self.customer_repo = customer_repo
        self.admin_repo = admin_repo

    def create_user(self, user_data):
        customer_data = user_data.pop('customer', None)
        user = self.user_repo.create_user(user_data)

        if user.user_type == 'customer' and customer_data:
            customer = self.customer_repo.create_customer(user, customer_data)
            user.customer = customer  
            user.save()
        
        elif user.user_type == 'admin':
            self.admin_repo.create_admin(user)

        return user

    def login_user(self, username, password):
        return self.user_repo.authenticate_user(username, password)

class UserLibraryService:
    def __init__(self, library_repo: IUserLibraryRepository):
        self.library_repo = library_repo

    def get_user_library(self, user):
        return {
            "purchased_games": self.library_repo.get_purchased_games(user),
            "rented_games": self.library_repo.get_rented_games(user),
            "shared_rentals": self.library_repo.get_shared_rentals(user),
        }
    
class UserSearchService:
    def __init__(self, user_search_repo):
        self.user_search_repo = user_search_repo

    def search_users(self, query: str, exclude_user_id: int):
        return self.user_search_repo.search_users(query, exclude_user_id)    