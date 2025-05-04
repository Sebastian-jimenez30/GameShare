# apps/transactions/interfaces.py

from abc import ABC, abstractmethod
from typing import List, Optional
from .models import (
    Rental, Transaction, SharedRental, SharedRentalPayment,
    Cart, CartItem, Invoice, Payment
)
from apps.users.models import User
from apps.games.models import Game


class IRentalRepository(ABC):
    @abstractmethod
    def create_rental(self, rental_data: dict) -> Rental:
        pass

    @abstractmethod
    def get_rental_by_id(self, rental_id: int) -> Optional[Rental]:
        pass

    @abstractmethod
    def update_rental(self, rental_id: int, rental_data: dict) -> Optional[Rental]:
        pass

    @abstractmethod
    def delete_rental(self, rental_id: int) -> bool:
        pass

    @abstractmethod
    def list_rentals(self) -> List[Rental]:
        pass


class IPurchaseRepository(ABC):

    @abstractmethod
    def purchase_exists(self, user: User, game: Game) -> bool:
        pass


class ISharedRentalRepository(ABC):
    @abstractmethod
    def create_shared_rental(self, shared_rental_data: dict) -> SharedRental:
        pass

    @abstractmethod
    def get_shared_rental_by_id(self, shared_rental_id: int) -> Optional[SharedRental]:
        pass

    @abstractmethod
    def update_shared_rental(self, shared_rental_id: int, data: dict) -> Optional[SharedRental]:
        pass

    @abstractmethod
    def delete_shared_rental(self, shared_rental_id: int) -> bool:
        pass

    @abstractmethod
    def list_shared_rentals(self, user: User) -> List[SharedRental]:
        pass


class ISharedRentalPaymentRepository(ABC):
    @abstractmethod
    def create_shared_rental_payment(self, payment_data: dict) -> SharedRentalPayment:
        pass

    @abstractmethod
    def get_shared_rental_payment_by_id(self, payment_id: int) -> Optional[SharedRentalPayment]:
        pass

    @abstractmethod
    def update_shared_rental_payment(self, payment_id: int, data: dict) -> Optional[SharedRentalPayment]:
        pass

    @abstractmethod
    def delete_shared_rental_payment(self, payment_id: int) -> bool:
        pass

    @abstractmethod
    def list_shared_rental_payments(self) -> List[SharedRentalPayment]:
        pass


class ICartRepository(ABC):
    @abstractmethod
    def create_cart(self, cart_data: dict) -> Cart:
        pass

    @abstractmethod
    def get_cart_by_id(self, cart_id: int) -> Optional[Cart]:
        pass

    @abstractmethod
    def get_cart_by_user(self, user: User) -> Optional[Cart]:
        pass

    @abstractmethod
    def update_cart(self, cart_id: int, cart_data: dict) -> Optional[Cart]:
        pass

    @abstractmethod
    def delete_cart(self, cart_id: int) -> bool:
        pass

    @abstractmethod
    def list_carts(self) -> List[Cart]:
        pass


class ICartItemRepository(ABC):
    @abstractmethod
    def create_cart_item(self, cart_item_data: dict) -> CartItem:
        pass

    @abstractmethod
    def get_cart_item_by_id(self, item_id: int) -> Optional[CartItem]:
        pass

    @abstractmethod
    def get_item_by_cart_and_game(self, cart: Cart, game: Game) -> Optional[CartItem]:
        pass

    @abstractmethod
    def update_cart_item(self, item_id: int, cart_item_data: dict) -> Optional[CartItem]:
        pass

    @abstractmethod
    def delete_cart_item(self, item_id: int) -> bool:
        pass

    @abstractmethod
    def list_cart_items(self) -> List[CartItem]:
        pass


class IInvoiceRepository(ABC):
    @abstractmethod
    def create_invoice(self, invoice_data: dict) -> Invoice:
        pass

    @abstractmethod
    def get_invoice_by_id(self, invoice_id: int) -> Optional[Invoice]:
        pass

    @abstractmethod
    def update_invoice(self, invoice_id: int, invoice_data: dict) -> Optional[Invoice]:
        pass

    @abstractmethod
    def delete_invoice(self, invoice_id: int) -> bool:
        pass

    @abstractmethod
    def list_invoices(self) -> List[Invoice]:
        pass


class IPaymentRepository(ABC):
    @abstractmethod
    def create_payment(self, payment_data: dict) -> Payment:
        pass

    @abstractmethod
    def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        pass

    @abstractmethod
    def update_payment(self, payment_id: int, payment_data: dict) -> Optional[Payment]:
        pass

    @abstractmethod
    def delete_payment(self, payment_id: int) -> bool:
        pass

    @abstractmethod
    def list_payments(self) -> List[Payment]:
        pass

class ITransactionRepository(ABC):
    @abstractmethod
    def create_transaction(self, transaction_data: dict) -> Transaction:
        pass

    @abstractmethod
    def get_transaction_by_id(self, transaction_id: int) -> Transaction:
        pass

    @abstractmethod
    def update_transaction(self, transaction_id: int, data: dict) -> Transaction:
        pass

    @abstractmethod
    def delete_transaction(self, transaction_id: int) -> bool:
        pass

    @abstractmethod
    def list_transactions(self) -> List[Transaction]:
        pass
