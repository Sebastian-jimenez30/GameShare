# apps/transactions/services.py

from typing import List
from decimal import Decimal
from django.utils.timezone import now
from datetime import timedelta

from apps.games.models import Game
from apps.users.models import User

from .interfaces import (
    IRentalRepository, IPurchaseRepository, ISharedRentalRepository,
    ISharedRentalPaymentRepository, ICartRepository, ICartItemRepository,
    IInvoiceRepository, IPaymentRepository
)

class TransactionService:
    def __init__(
        self,
        rental_repo: IRentalRepository,
        purchase_repo: IPurchaseRepository,
        shared_rental_repo: ISharedRentalRepository,
        shared_payment_repo: ISharedRentalPaymentRepository,
        cart_repo: ICartRepository,
        cart_item_repo: ICartItemRepository,
        invoice_repo: IInvoiceRepository,
        payment_repo: IPaymentRepository,
    ):
        self.rental_repo = rental_repo
        self.purchase_repo = purchase_repo
        self.shared_rental_repo = shared_rental_repo
        self.shared_payment_repo = shared_payment_repo
        self.cart_repo = cart_repo
        self.cart_item_repo = cart_item_repo
        self.invoice_repo = invoice_repo
        self.payment_repo = payment_repo

    def get_or_create_cart_for_user(self, user: User):
        cart = self.cart_repo.get_cart_by_user(user)
        if not cart:
            cart = self.cart_repo.create_cart({'user': user, 'total': Decimal('0.00')})
        return cart

    def checkout_cart(self, user: User):
        cart = self.get_or_create_cart_for_user(user)
        items = cart.cartitem_set.all()

        if not items:
            raise ValueError("El carrito está vacío.")

        for item in items:
            if item.item_type == 'purchase':
                self.purchase_repo.create_purchase({
                    'user': user,
                    'game': item.game,
                    'date': now()
                })

            elif item.item_type == 'rent':
                self.rental_repo.create_rental({
                    'user': user,
                    'game': item.game,
                    'start_date': now(),
                    'end_date': now() + timedelta(days=7),
                    'total_price': item.game.price,
                    'status': 'active'
                })

            elif item.item_type == 'shared':
                shared_users = list(item.shared_users.all())
                if user not in shared_users:
                    shared_users.append(user)
                self.create_shared_rental_with_payments(item.game, shared_users)

        items.delete()
        cart.total = Decimal('0.00')
        cart.save()

    def create_shared_rental_with_payments(self, game: Game, users: List[User]):
        if not users:
            raise ValueError("La lista de usuarios no puede estar vacía.")
        if not game.price:
            raise ValueError("El juego no tiene precio definido.")

        total_amount = Decimal(game.price)
        amount_per_user = total_amount / Decimal(len(users))

        shared_rental = self.shared_rental_repo.create_shared_rental({'game': game})

        for user in users:
            self.shared_payment_repo.create_shared_rental_payment({
                'shared_rental': shared_rental,
                'user': user,
                'amount': amount_per_user,
                'status': 'pending'
            })

        return shared_rental

    def add_item_to_cart_by_game_id(self, user_id: int, game_id: int, item_type: str, quantity: int = 1):
        user = User.objects.get(id=user_id)
        game = Game.objects.get(id=game_id)

        if self.purchase_repo.purchase_exists(user, game):
            raise ValueError("El juego ya fue comprado.")

        cart = self.get_or_create_cart_for_user(user)
        existing_item = self.cart_item_repo.get_item_by_cart_and_game(cart, game)

        if existing_item:
            existing_item.quantity += quantity
            existing_item.save()
        else:
            self.cart_item_repo.create_cart_item({
                'cart': cart,
                'game': game,
                'item_type': item_type,
                'quantity': quantity
            })

        self.update_cart_total(cart)

    def remove_item_from_cart(self, cart_item_id: int):
        item = self.cart_item_repo.get_cart_item_by_id(cart_item_id)
        if item:
            cart = item.cart
            self.cart_item_repo.delete_cart_item(cart_item_id)
            self.update_cart_total(cart)
        else:
            raise ValueError("El ítem no existe en el carrito.")

    def update_cart_total(self, cart):
        total = sum(item.game.price * item.quantity for item in cart.cartitem_set.all())
        cart.total = total
        cart.save()

    def complete_payment(self, user: User, amount: Decimal, method: str):
        payment = self.payment_repo.create_payment({
            'user': user,
            'amount': amount,
            'method': method,
            'status': 'completed',
            'date': now()
        })
        return payment