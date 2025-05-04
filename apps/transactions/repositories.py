# apps/transactions/repositories.py

from typing import List, Optional
from django.core.exceptions import ObjectDoesNotExist

from apps.users.models import User
from apps.games.models import Game

from .models import (
    Rental, Transaction, SharedRental, SharedRentalPayment,
    Cart, CartItem, Invoice, Payment
)
from .interfaces import (
    IRentalRepository, IPurchaseRepository, ISharedRentalRepository,
    ISharedRentalPaymentRepository, ICartRepository, ICartItemRepository,
    IInvoiceRepository, IPaymentRepository
)


class RentalRepository(IRentalRepository):
    def create_rental(self, rental_data: dict) -> Rental:
        return Rental.objects.create(**rental_data)

    def get_rental_by_id(self, rental_id: int) -> Optional[Rental]:
        return Rental.objects.filter(id=rental_id).first()

    def update_rental(self, rental_id: int, rental_data: dict) -> Optional[Rental]:
        rental = self.get_rental_by_id(rental_id)
        if rental:
            for field, value in rental_data.items():
                setattr(rental, field, value)
            rental.save()
        return rental

    def delete_rental(self, rental_id: int) -> bool:
        return Rental.objects.filter(id=rental_id).delete()[0] > 0

    def list_rentals(self) -> List[Rental]:
        return list(Rental.objects.all())


class SharedRentalRepository(ISharedRentalRepository):
    def create_shared_rental(self, shared_rental_data: dict) -> SharedRental:
        """
        Crea un alquiler compartido y lo asocia con los usuarios correctos.
        """
        users = shared_rental_data.pop("users", [])
        shared_rental = SharedRental.objects.create(**shared_rental_data)

        for user in users:
            SharedRentalPayment.objects.create(
                shared_rental=shared_rental,
                user=user,
                amount=shared_rental.game.price / len(users),
                status="pending"
            )

        return shared_rental

    def get_shared_rental_by_id(self, shared_rental_id: int) -> Optional[SharedRental]:
        return SharedRental.objects.filter(id=shared_rental_id).select_related("game").first()

    def delete_shared_rental(self, shared_rental_id: int) -> bool:
        deleted, _ = SharedRental.objects.filter(id=shared_rental_id).delete()
        return deleted > 0

    def list_shared_rentals(self, user: User) -> List[SharedRental]:
        """
        Retorna solo las rentas compartidas en las que el usuario está involucrado.
        """
        shared_rental_ids = SharedRentalPayment.objects.filter(user=user).values_list("shared_rental_id", flat=True)
        return list(SharedRental.objects.filter(id__in=shared_rental_ids).select_related("game"))

    def update_shared_rental(self, shared_rental_id: int, data: dict) -> Optional[SharedRental]:
        shared_rental = self.get_shared_rental_by_id(shared_rental_id)
        if shared_rental:
            for field, value in data.items():
                setattr(shared_rental, field, value)
            shared_rental.save()
        return shared_rental


class SharedRentalPaymentRepository(ISharedRentalPaymentRepository):
    def create_shared_rental_payment(self, payment_data: dict) -> SharedRentalPayment:
        return SharedRentalPayment.objects.create(**payment_data)

    def get_shared_rental_payment_by_id(self, payment_id: int) -> Optional[SharedRentalPayment]:
        return SharedRentalPayment.objects.filter(id=payment_id).first()

    def update_shared_rental_payment(self, payment_id: int, data: dict) -> Optional[SharedRentalPayment]:
        payment = self.get_shared_rental_payment_by_id(payment_id)
        if payment:
            for field, value in data.items():
                setattr(payment, field, value)
            payment.save()
        return payment

    def delete_shared_rental_payment(self, payment_id: int) -> bool:
        deleted, _ = SharedRentalPayment.objects.filter(id=payment_id).delete()
        return deleted > 0

    def list_shared_rental_payments(self) -> List[SharedRentalPayment]:
        return list(SharedRentalPayment.objects.all())



class CartRepository(ICartRepository):
    def create_cart(self, cart_data: dict) -> Cart:
        return Cart.objects.create(**cart_data)

    def get_cart_by_id(self, cart_id: int) -> Optional[Cart]:
        return Cart.objects.filter(id=cart_id).first()

    def get_cart_by_user(self, user: User) -> Optional[Cart]:
        return Cart.objects.filter(user=user).first()

    def delete_cart(self, cart_id: int) -> bool:
        deleted, _ = Cart.objects.filter(id=cart_id).delete()
        return deleted > 0

    def list_carts(self) -> List[Cart]:
        return list(Cart.objects.all())

    def update_cart(self, cart_id: int, cart_data: dict) -> Optional[Cart]:
        cart = self.get_cart_by_id(cart_id)
        if cart:
            for field, value in cart_data.items():
                setattr(cart, field, value)
            cart.save()
        return cart



class CartItemRepository(ICartItemRepository):
    def create_cart_item(self, cart_item_data: dict) -> CartItem:
        return CartItem.objects.create(**cart_item_data)

    def get_cart_item_by_id(self, item_id: int) -> Optional[CartItem]:
        return CartItem.objects.filter(id=item_id).first()

    def get_item_by_cart_and_game(self, cart: Cart, game: Game) -> Optional[CartItem]:
        return CartItem.objects.filter(cart=cart, game=game).first()

    def delete_cart_item(self, item_id: int) -> bool:
        deleted, _ = CartItem.objects.filter(id=item_id).delete()
        return deleted > 0

    def list_cart_items(self) -> List[CartItem]:
        return list(CartItem.objects.all())

    def update_cart_item(self, item_id: int, cart_item_data: dict) -> Optional[CartItem]:
        item = self.get_cart_item_by_id(item_id)
        if item:
            for field, value in cart_item_data.items():
                setattr(item, field, value)
            item.save()
        return item


class InvoiceRepository(IInvoiceRepository):
    def create_invoice(self, invoice_data: dict) -> Invoice:
        return Invoice.objects.create(**invoice_data)

    def get_invoice_by_id(self, invoice_id: int) -> Optional[Invoice]:
        return Invoice.objects.filter(id=invoice_id).first()

    def delete_invoice(self, invoice_id: int) -> bool:
        deleted, _ = Invoice.objects.filter(id=invoice_id).delete()
        return deleted > 0

    def list_invoices(self) -> List[Invoice]:
        return list(Invoice.objects.all())

    def update_invoice(self, invoice_id: int, invoice_data: dict) -> Optional[Invoice]:
        invoice = self.get_invoice_by_id(invoice_id)
        if invoice:
            for field, value in invoice_data.items():
                setattr(invoice, field, value)
            invoice.save()
        return invoice


class PaymentRepository(IPaymentRepository):
    def create_payment(self, payment_data: dict) -> Payment:
        return Payment.objects.create(**payment_data)

    def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        return Payment.objects.filter(id=payment_id).first()

    # Métodos faltantes añadidos:
    def delete_payment(self, payment_id: int) -> bool:
        deleted, _ = Payment.objects.filter(id=payment_id).delete()
        return deleted > 0

    def list_payments(self) -> List[Payment]:
        return list(Payment.objects.all())

    def update_payment(self, payment_id: int, payment_data: dict) -> Optional[Payment]:
        payment = self.get_payment_by_id(payment_id)
        if payment:
            for field, value in payment_data.items():
                setattr(payment, field, value)
            payment.save()
        return payment
    
from apps.transactions.models import Transaction

class TransactionRepository:
    def create_transaction(self, transaction_data: dict) -> Transaction:
        return Transaction.objects.create(**transaction_data)

    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        return Transaction.objects.filter(id=transaction_id).first()

    def transaction_exists(self, user: User, game: Game, transaction_type: str) -> bool:
        return Transaction.objects.filter(user=user, game=game, transaction_type=transaction_type).exists()

    def list_transactions(self) -> List[Transaction]:
        return list(Transaction.objects.all())

    def delete_transaction(self, transaction_id: int) -> bool:
        deleted, _ = Transaction.objects.filter(id=transaction_id).delete()
        return deleted > 0

    def update_transaction(self, transaction_id: int, transaction_data: dict) -> Optional[Transaction]:
        transaction = self.get_transaction_by_id(transaction_id)
        if transaction:
            for field, value in transaction_data.items():
                setattr(transaction, field, value)
            transaction.save()
        return transaction
