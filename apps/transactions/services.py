from typing import List
from decimal import Decimal
from django.utils.timezone import now
from datetime import timedelta

from apps.games.models import Game
from apps.users.models import User

from .models import Transaction
from .interfaces import (
    IRentalRepository, ISharedRentalRepository,
    ISharedRentalPaymentRepository, ICartRepository, ICartItemRepository,
    IInvoiceRepository, IPaymentRepository
)

class TransactionService:
    def __init__(
        self,
        rental_repo: IRentalRepository,
        shared_rental_repo: ISharedRentalRepository,
        shared_payment_repo: ISharedRentalPaymentRepository,
        cart_repo: ICartRepository,
        cart_item_repo: ICartItemRepository,
        invoice_repo: IInvoiceRepository,
        payment_repo: IPaymentRepository,
    ):
        self.rental_repo = rental_repo
        self.shared_rental_repo = shared_rental_repo
        self.shared_payment_repo = shared_payment_repo
        self.cart_repo = cart_repo
        self.cart_item_repo = cart_item_repo
        self.invoice_repo = invoice_repo
        self.payment_repo = payment_repo

    def get_or_create_cart_for_user(self, user: User):
        cart = self.cart_repo.get_cart_by_user(user)
        if not cart:
            cart = self.cart_repo.create_cart({'user': user})
        return cart

    def checkout_cart(self, user: User):
        cart = self.get_or_create_cart_for_user(user)
        items = cart.items.all()

        if not items:
            raise ValueError("El carrito está vacío.")

        for item in items:
            transaction = Transaction.objects.create(
                user=user,
                game=item.game,
                transaction_type=item.item_type if item.item_type != 'shared' else 'shared_rental',
                total_price=item.get_total_price()
            )

            if item.item_type == 'rental':
                self.rental_repo.create_rental({
                    'transaction': transaction,
                    'rental_type': item.rental_type or 'daily',
                    'start_time': now(),
                    'end_time': now() + timedelta(days=1 if item.rental_type == 'daily' else 0, hours=1 if item.rental_type == 'hourly' else 0),
                    'status': 'active'
                })

            elif item.item_type == 'shared':
                shared_users = list(item.shared_with.all())
                if user not in shared_users:
                    shared_users.append(user)
                self.create_shared_rental_with_payments(item.game, shared_users)

            # En todos los casos se genera factura (excepto shared, que se maneja por pagos separados)
            if item.item_type in ['purchase', 'rental']:
                self.invoice_repo.create_invoice({
                    'user': user,
                    'transaction': transaction,
                    'total': transaction.total_price,
                    'pdf_file': 'invoices/dummy.pdf'  # Temporal, luego se genera real
                })

        items.delete()

    def create_shared_rental_with_payments(self, game: Game, users: List[User]):
        if not users:
            raise ValueError("La lista de usuarios no puede estar vacía.")

        total_amount = game.purchase_price
        shared_rental = self.shared_rental_repo.create_shared_rental({
            'game': game,
            'created_by': users[0],
            'start_time': now(),
            'end_time': now() + timedelta(days=3),
            'total_cost': total_amount,
            'users': users
        })
        return shared_rental

    def add_item_to_cart_by_game_id(self, user_id: int, game_id: int, item_type: str, quantity: int = 1, rental_type: str = None):
        user = User.objects.get(id=user_id)
        game = Game.objects.get(id=game_id)

        if item_type == 'purchase' and Transaction.objects.filter(user=user, game=game, transaction_type='purchase').exists():
            raise ValueError("El juego ya fue comprado.")

        cart = self.get_or_create_cart_for_user(user)
        existing_item = self.cart_item_repo.get_item_by_cart_and_game(cart, game)

        if existing_item:
            existing_item.quantity += quantity
            if rental_type:
                existing_item.rental_type = rental_type
            existing_item.save()
        else:
            self.cart_item_repo.create_cart_item({
                'cart': cart,
                'game': game,
                'item_type': item_type,
                'quantity': quantity,
                'rental_type': rental_type
            })

    def remove_item_from_cart(self, cart_item_id: int):
        item = self.cart_item_repo.get_cart_item_by_id(cart_item_id)
        if item:
            self.cart_item_repo.delete_cart_item(cart_item_id)
        else:
            raise ValueError("El ítem no existe en el carrito.")

    def complete_payment(self, user: User, amount: Decimal, method: str):
        return self.payment_repo.create_payment({
            'user': user,
            'amount': amount,
            'method': method,
            'status': 'completed',
            'date': now()
        })

    def update_cart_total(self, cart):
        total = sum(item.get_total_price() for item in cart.items.all())
        cart.total = total
        cart.save()
