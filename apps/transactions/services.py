from typing import List
from decimal import Decimal
from django.utils.timezone import now
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from io import BytesIO

from apps.games.models import Game
from apps.users.models import User
from apps.transactions.models import Invoice, CartItem

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

    def process_checkout(self, user: User, items: List[CartItem]):
        last_invoice = None

        if not items:
            raise ValueError("El carrito está vacío.")

        for item in items:
            total_price = self.cart_item_repo.get_total_price(item)

            transaction = Transaction.objects.create(
                user=user,
                game=item.game,
                transaction_type=item.item_type if item.item_type != 'shared' else 'shared_rental',
                total_price=total_price
            )

            if item.item_type in ['rental', 'shared']:
                rental_data = {
                    'transaction': transaction,
                    'rental_type': item.rental_type or 'daily',
                    'start_time': now(),
                    'end_time': self.rental_repo.calcular_end_time(
                        item.rental_type or 'daily',
                        item.duration or 1,
                        now()
                    ),
                    'status': 'active'
                }

                if item.item_type == 'shared':
                    shared_users = list(item.shared_with.all())
                    if user not in shared_users:
                        shared_users.append(user)
                    self.create_shared_rental_with_payments(item, shared_users)
                else:
                    self.rental_repo.create_rental(rental_data)

            invoice = self.invoice_repo.create_invoice({
                'user': user,
                'transaction': transaction,
                'total': transaction.total_price,
                'pdf_file': None
            })
            pdf_file = self._generate_invoice_pdf(invoice)
            invoice.pdf_file.save(pdf_file.name, pdf_file, save=True)
            last_invoice = invoice

            # Eliminar cada ítem individualmente para no perder referencias
            self.cart_item_repo.delete_cart_item(item.id)

        return last_invoice

    def checkout_cart(self, user: User):
        cart = self.get_or_create_cart_for_user(user)
        items = cart.items.all()
        
        if not items:
            raise ValueError("El carrito está vacío.")

        total = sum([self.cart_item_repo.get_total_price(i) for i in items])

        return {
            "cart": cart,
            "items": items,
            "total": total
        }

    def add_item_to_cart_by_game_id(
        self,
        user_id: int,
        game_id: int,
        item_type: str,
        quantity: int = 1,
        rental_type: str = None,
        duration: int = None
    ):
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
            if duration:
                existing_item.duration = duration
            existing_item.save()
        else:
            self.cart_item_repo.create_cart_item({
                'cart': cart,
                'game': game,
                'item_type': item_type,
                'quantity': quantity,
                'rental_type': rental_type,
                'duration': duration
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
        total = Decimal('0.00')
        for item in cart.items.all():
            total += self.cart_item_repo.get_total_price(item)
        cart.total = total
        cart.save()

    def create_shared_rental_with_payments(self, item, users: List[User]):
        base_total = self.cart_item_repo.get_total_price(item)
        total_cost = base_total
        per_user = base_total / Decimal(len(users))

        shared_rental = self.shared_rental_repo.create_shared_rental({
            'game': item.game,
            'created_by': users[0],
            'start_time': now(),
            'end_time': self.rental_repo.calcular_end_time(
                item.rental_type or 'daily',
                item.duration or 1,
                now()
            ),
            'total_cost': total_cost,
            'users': users
        })

        for user in users:
            # Evita duplicados usando get_or_create
            self.shared_payment_repo.get_or_create_shared_rental_payment(
                shared_rental=shared_rental,
                user=user,
                defaults={
                    'amount': per_user,
                    'status': 'pending'
                }
            )

        return shared_rental

    def _generate_invoice_pdf(self, invoice: Invoice) -> ContentFile:
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, 760, f"Factura Electrónica N.º {invoice.id}")
        
        p.setFont("Helvetica", 10)
        p.drawString(50, 740, f"Fecha de emisión: {invoice.date.strftime('%Y-%m-%d %H:%M')}")
        p.drawString(50, 725, f"Cliente: {invoice.user.full_name} ({invoice.user.username})")
        p.drawString(50, 710, "NIT: 123456789-0")
        p.drawString(50, 695, "Dirección: Calle 123 #45-67, Bogotá")
        
        p.line(45, 685, 550, 685)
        p.drawString(50, 670, f"Juego: {invoice.transaction.game.title}")
        p.drawString(50, 655, f"Tipo de transacción: {invoice.transaction.transaction_type}")

        if invoice.transaction.transaction_type in ['rental', 'shared_rental']:
            rental = getattr(invoice.transaction, 'rental_detail', None)
            if rental:
                p.drawString(50, 640, f"Duración: {rental.duration} unidades")
                p.drawString(50, 625, f"Tipo de renta: {rental.rental_type}")

        p.line(45, 610, 550, 610)

        p.setFont("Helvetica-Bold", 12)
        subtotal = invoice.total / Decimal("1.19")
        iva = invoice.total - subtotal
        p.drawString(50, 590, f"Subtotal: ${subtotal:.2f}")
        p.drawString(50, 575, f"IVA (19%): ${iva:.2f}")
        p.drawString(50, 560, f"Total a pagar: ${invoice.total:.2f}")

        p.line(45, 550, 550, 550)
        p.drawString(50, 530, "Gracias por su compra en GameShare. Esta es una factura válida para efectos fiscales.")

        p.showPage()
        p.save()

        pdf_data = buffer.getvalue()
        buffer.close()
        return ContentFile(pdf_data, name=f"invoice_{invoice.id}.pdf")

