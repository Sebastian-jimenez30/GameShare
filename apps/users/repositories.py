from .models import User
from .interfaces import IUserRepository, IUserLibraryRepository, IUserSearchRepository
from django.contrib.auth import authenticate
from apps.transactions.models import Transaction, SharedRentalPayment
from django.db.models import Q
from typing import List
from django.utils.timezone import now


class UserRepository(IUserRepository):
    def create_user(self, user_data):
        return User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            full_name=user_data.get('full_name', ''),
            user_type=user_data.get('user_type', 'customer'),
            processor=user_data.get('processor', ''),
            ram_gb=user_data.get('ram_gb', 0),
            graphics_card=user_data.get('graphics_card', '')
        )

    def get_user_by_id(self, user_id: int):
        return User.objects.filter(id=user_id).first()

    def authenticate_user(self, username: str, password: str):
        return authenticate(username=username, password=password)
    
    def list_all_users(self) -> List[User]:
        return self.user_repo.list_all_users()



class UserLibraryRepository(IUserLibraryRepository):
    def get_purchased_games(self, user):
        purchases = Transaction.objects.filter(
            user=user, transaction_type='purchase'
        ).select_related('game')
        return [t.game for t in purchases]

    def get_rented_games(self, user):
        from apps.transactions.models import Rental

        active_rentals = Rental.objects.filter(
            transaction__user=user,
            transaction__transaction_type='rental',
            end_time__gt=now()
        ).select_related('transaction__game')

        return [r.transaction.game for r in active_rentals]
    
    def get_shared_rentals(self, user):
        from django.utils.timezone import now

        shared_payments = SharedRentalPayment.objects.filter(
            user=user
        ).select_related('shared_rental__game')

        available_shared_rentals = []
        unavailable_shared_rentals = []

        for payment in shared_payments:
            shared_rental = payment.shared_rental
            if shared_rental.end_time <= now():
                continue  # saltar si ya venció

            payments = shared_rental.payments.all()
            all_paid = all(p.status == 'completed' for p in payments)

            if all_paid:
                available_shared_rentals.append(shared_rental)
            else:
                unavailable_shared_rentals.append(shared_rental)

        return {
            "available": available_shared_rentals,
            "unavailable": unavailable_shared_rentals
        }


class UserSearchRepository(IUserSearchRepository):
    def search_users(self, query: str, exclude_user_id: int):
        return User.objects.filter(
            Q(username__icontains=query) | Q(full_name__icontains=query)
        ).exclude(id=exclude_user_id)[:10]
