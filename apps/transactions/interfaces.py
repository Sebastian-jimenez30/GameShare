# apps/transactions/interfaces.py

from abc import ABC, abstractmethod
from typing import List
from .models import (
    Rental, Purchase, SharedRental, SharedRentalPayment,
    Cart, CartItem, Invoice, Payment
)


class IRentalRepository(ABC):
    @abstractmethod
    def create_rental(self, rental_data: dict) -> Rental:
        pass

    @abstractmethod
    def get_rental_by_id(self, rental_id: int) -> Rental:
        pass

    @abstractmethod
    def update_rental(self, rental_id: int, rental_data: dict) -> Rental:
        pass

    @abstractmethod
    def delete_rental(self, rental_id: int) -> bool:
        pass

    @abstractmethod
    def list_rentals(self) -> List[Rental]:
        pass


class IPurchaseRepository(ABC):
    @abstractmethod
    def create_purchase(self, purchase_data: dict) -> Purchase:
        pass

    @abstractmethod
    def get_purchase_by_id(self, purchase_id: int) -> Purchase:
        pass

    @abstractmethod
    def update_purchase(self, purchase_id: int, purchase_data: dict) -> Purchase:
        pass

    @abstractmethod
    def delete_purchase(self, purchase_id: int) -> bool:
        pass

    @abstractmethod
    def list_purchases(self) -> List[Purchase]:
        pass


class ISharedRentalRepository(ABC):
    @abstractmethod
    def create_shared_rental(self, shared_rental_data: dict) -> SharedRental:
        pass

    @abstractmethod
    def get_shared_rental_by_id(self, shared_rental_id: int) -> SharedRental:
        pass

    @abstractmethod
    def update_shared_rental(self, shared_rental_id: int, data: dict) -> SharedRental:
        pass

    @abstractmethod
    def delete_shared_rental(self, shared_rental_id: int) -> bool:
        pass

    @abstractmethod
    def list_shared_rentals(self) -> List[SharedRental]:
        pass


class ISharedRentalPaymentRepository(ABC):
    @abstractmethod
    def create_shared_rental_payment(self, payment_data: dict) -> SharedRentalPayment:
        pass

    @abstractmethod
    def get_shared_rental_payment_by_id(self, payment_id: int) -> SharedRentalPayment:
        pass

    @abstractmethod
    def update_shared_rental_payment(self, payment_id: int, data: dict) -> SharedRentalPayment:
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
    def get_cart_by_id(self, cart_id: int) -> Cart:
        pass

    @abstractmethod
    def update_cart(self, cart_id: int, cart_data: dict) -> Cart:
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
    def get_cart_item_by_id(self, item_id: int) -> CartItem:
        pass

    @abstractmethod
    def update_cart_item(self, item_id: int, cart_item_data: dict) -> CartItem:
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
    def get_invoice_by_id(self, invoice_id: int) -> Invoice:
        pass

    @abstractmethod
    def update_invoice(self, invoice_id: int, invoice_data: dict) -> Invoice:
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
    def get_payment_by_id(self, payment_id: int) -> Payment:
        pass

    @abstractmethod
    def update_payment(self, payment_id: int, payment_data: dict) -> Payment:
        pass

    @abstractmethod
    def delete_payment(self, payment_id: int) -> bool:
        pass

    @abstractmethod
    def list_payments(self) -> List[Payment]:
        pass