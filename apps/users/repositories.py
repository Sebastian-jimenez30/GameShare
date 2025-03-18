from .models import User, Customer, AdminProfile
from .interfaces import IUserRepository, ICustomerRepository, IAdminRepository, IUserLibraryRepository, IUserSearchRepository
from django.contrib.auth import authenticate
from apps.games.models import Game
from apps.transactions.models import Purchase, Rental, SharedRental, SharedRentalPayment
from django.db.models import Q

class UserRepository(IUserRepository):
    def create_user(self, user_data):
        return User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            name=user_data['name'],
            user_type=user_data.get('user_type', 'customer')
        )

    def get_user_by_id(self, user_id: int):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
    
    def authenticate_user(self, username: str, password: str):
        return authenticate(username=username, password=password)  

        
class CustomerRepository(ICustomerRepository):
    def create_customer(self, user: User, customer_data: dict):
        return Customer.objects.create(user=user, **customer_data)

class AdminRepository(IAdminRepository):
    def create_admin(self, user: User):
        return AdminProfile.objects.create(user=user)
    
class UserLibraryRepository(IUserLibraryRepository):
    def get_purchased_games(self, user):
        purchases = Purchase.objects.filter(user=user).select_related('game')
        return [purchase.game for purchase in purchases]

    def get_rented_games(self, user):
        rentals = Rental.objects.filter(user=user).select_related('game')
        return [rental.game for rental in rentals]

    def get_shared_rentals(self, user):
        shared_rentals = SharedRental.objects.filter(users=user).select_related('game')

        available_shared_rentals = []
        unavailable_shared_rentals = []

        for shared_rental in shared_rentals:
            payments = SharedRentalPayment.objects.filter(shared_rental=shared_rental)
            all_paid = not payments.filter(~Q(status='completed')).exists()

            if all_paid:
                available_shared_rentals.append(shared_rental.game)
            else:
                unavailable_shared_rentals.append(shared_rental.game)

        return {
            "available": available_shared_rentals,
            "unavailable": unavailable_shared_rentals
        }

class UserSearchRepository(IUserSearchRepository):
    def search_users(self, query: str, exclude_user_id: int):
        return User.objects.filter(username__icontains=query).exclude(id=exclude_user_id)[:10]