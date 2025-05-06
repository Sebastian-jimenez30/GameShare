from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView
from django.views import View
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.http import Http404, HttpResponse
from decimal import Decimal
from django.utils.timezone import now

from .models import SharedRental
from .services import TransactionService
from .repositories import (
    RentalRepository, SharedRentalRepository,
    SharedRentalPaymentRepository, CartRepository, CartItemRepository,
    InvoiceRepository, PaymentRepository, InvoiceRepository
)

import logging
logger = logging.getLogger(__name__)

User = get_user_model()


invoice_repo = InvoiceRepository()

transaction_service = TransactionService(
    rental_repo=RentalRepository(),
    shared_rental_repo=SharedRentalRepository(),
    shared_payment_repo=SharedRentalPaymentRepository(),
    cart_repo=CartRepository(),
    cart_item_repo=CartItemRepository(),
    invoice_repo=InvoiceRepository(),
    payment_repo=PaymentRepository()
)

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        game_id = request.POST.get('game_id')
        item_type = request.POST.get('item_type')
        rental_type = request.POST.get('rental_type')  # Puede ser None

        try:
            duration = int(request.POST.get('duration', 1))
            if duration < 1:
                raise ValueError("La duración debe ser mayor que cero.")
        except (ValueError, TypeError):
            duration = 1  # Valor por defecto si no se especifica o es inválido

        try:
            transaction_service.add_item_to_cart_by_game_id(
                user_id=request.user.id,
                game_id=game_id,
                item_type=item_type,
                quantity=1,
                rental_type=rental_type,
                duration=duration
            )
            messages.success(request, "Juego añadido correctamente al carrito.")
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('catalog')

class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/cart_view.html'
    login_url = 'user_login_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = transaction_service.get_or_create_cart_for_user(self.request.user)
        items = cart.items.all()

        item_data = []
        for item in items:
            base_price = transaction_service.cart_item_repo.get_total_price(item)
            if item.item_type == 'shared':
                price = base_price
            else:
                price = base_price
            item_data.append({'obj': item, 'price': price})

        total = sum(entry['price'] for entry in item_data)

        context.update({
            'cart': cart,
            'items': item_data,
            'cart_total_amount': total
        })
        return context

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        try:
            transaction_service.remove_item_from_cart(item_id)
            messages.success(request, "Ítem eliminado del carrito.")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('cart_view')

class CheckoutCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            cart_data = transaction_service.checkout_cart(request.user)
            request.session['cart_pending'] = True  # Marcar que hay una compra en espera
            messages.info(request, "Por favor confirma el método de pago.")
            return redirect('billing_summary')  # o con un ID si necesitas
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('cart_view')


class SharedRentalDetailsView(LoginRequiredMixin, DetailView):
    model = SharedRental
    template_name = 'transactions/shared_rental_details.html'
    context_object_name = 'shared_rental'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shared_rental = self.get_object()
        payments = shared_rental.payments.all()
        user_payment = payments.filter(user=self.request.user).first()

        context.update({
            'paid_users': payments.filter(status='completed'),
            'pending_users': payments.filter(status='pending'),
            'user_has_paid': user_payment.status == 'completed' if user_payment else False,
            'user_payment_id': user_payment.id if user_payment else None
        })
        return context

class CompleteSharedPaymentView(LoginRequiredMixin, View):
    def post(self, request, payment_id):
        payment = transaction_service.shared_payment_repo.get_shared_rental_payment_by_id(payment_id)

        if not payment:
            messages.error(request, "El pago no existe.")
            return redirect('user_library')

        if payment.status == 'completed':
            messages.info(request, "Este pago ya ha sido completado.")
        else:
            payment.status = 'completed'
            payment.payment_date = now()
            payment.save()
            messages.success(request, "Pago completado exitosamente.")

        return redirect('shared_rental_details', pk=payment.shared_rental.id)

class UpdateCartItemTypeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        new_type = request.POST.get('item_type')

        try:
            item = transaction_service.cart_item_repo.get_cart_item_by_id(item_id)
            if not item or item.cart.user != request.user:
                messages.error(request, "Ítem no encontrado o acceso denegado.")
                return redirect('cart_view')

            if new_type in ['purchase', 'rental', 'shared']:
                transaction_service.cart_item_repo.update_cart_item(item_id, {'item_type': new_type})
                transaction_service.update_cart_total(item.cart)
                messages.success(request, "Tipo de ítem actualizado correctamente.")
            else:
                messages.error(request, "Tipo de ítem inválido.")
        except Exception as e:
            messages.error(request, str(e))

        return redirect('cart_view')

class UpdateCartItemSharedUsersView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        usernames = [u.strip() for u in request.POST.get('usernames', '').split(',') if u.strip()]

        try:
            item = transaction_service.cart_item_repo.get_cart_item_by_id(item_id)
            if not item or item.cart.user != request.user:
                messages.error(request, "Ítem no encontrado o acceso denegado.")
                return redirect('cart_view')

            if item.item_type != 'shared':
                messages.error(request, "Este ítem no es de tipo compartido.")
                return redirect('cart_view')

            new_users = User.objects.filter(username__in=usernames).exclude(id=request.user.id).distinct()
            combined_users = set(item.shared_with.all()).union(new_users)

            if len(combined_users) > 4:
                messages.warning(request, "No puedes compartir con más de 4 usuarios.")
                return redirect('cart_view')

            item.shared_with.set(combined_users)
            item.save()

            messages.success(request, "Usuarios añadidos correctamente.")
        except Exception as e:
            messages.error(request, str(e))

        return redirect('cart_view')

class RemoveSharedUserFromCartItemView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        user_id = kwargs.get('user_id')

        try:
            item = transaction_service.cart_item_repo.get_cart_item_by_id(item_id)
            user_to_remove = User.objects.filter(id=user_id).first()

            if not item or item.cart.user != request.user or not user_to_remove:
                messages.error(request, "Ítem o usuario no encontrado, o acceso denegado.")
                return redirect('cart_view')

            item.shared_with.remove(user_to_remove)
            item.save()

            messages.success(request, f"Usuario {user_to_remove.username} eliminado del grupo compartido.")
        except Exception as e:
            messages.error(request, str(e))

        return redirect('cart_view')

class UpdateCartItemQuantityView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')

        # Validar duración
        try:
            duration = int(request.POST.get('duration', 1))
            if duration < 1:
                raise ValueError("La duración debe ser mayor que cero.")
        except (ValueError, TypeError):
            messages.error(request, "Duración inválida.")
            return redirect('cart_view')

        # Capturar tipo de renta y normalizar 'None' como None
        rental_type = request.POST.get('rental_type')
        if rental_type == 'None':
            rental_type = None

        # Obtener ítem
        item = transaction_service.cart_item_repo.get_cart_item_by_id(item_id)
        if not item or item.cart.user != request.user:
            messages.error(request, "Ítem no encontrado o acceso denegado.")
            return redirect('cart_view')

        # Log para debug
        logger.debug(f"[DEBUG] Actualizando item {item_id} con: "
                     f"{{'duration': {duration}, 'rental_type': {rental_type}, 'quantity': 1}}")

        # Actualizar ítem
        transaction_service.cart_item_repo.update_cart_item(item_id, {
            'duration': duration,
            'rental_type': rental_type,
            'quantity': 1
        })

        # Recalcular total
        transaction_service.update_cart_total(item.cart)

        messages.success(request, "Duración y tipo de renta actualizados correctamente.")
        return redirect('cart_view')

class InvoiceDownloadView(LoginRequiredMixin, View):
    def get(self, request, invoice_id):
        invoice = invoice_repo.get_invoice_by_id(invoice_id)

        if not invoice or invoice.user != request.user:
            raise Http404("Factura no encontrada o acceso denegado.")

        if not invoice.pdf_file:
            # Usar el método interno del servicio
            pdf_file = transaction_service._generate_invoice_pdf(invoice)
            invoice.pdf_file.save(pdf_file.name, pdf_file, save=True)

        response = HttpResponse(invoice.pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{invoice.pdf_file.name}"'
        return response

class BillingView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/billing_summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = transaction_service.get_or_create_cart_for_user(self.request.user)
        items = cart.items.all()
        if not items:
            raise Http404("No hay ítems pendientes para facturar.")

        total = sum(transaction_service.cart_item_repo.get_total_price(item) for item in items)
        subtotal = (total / Decimal('1.19')).quantize(Decimal('0.01'))
        iva = (total - subtotal).quantize(Decimal('0.01'))

        context.update({
            'items': items,
            'total': total,
            'subtotal': subtotal,
            'iva': iva,
            'payment_methods': ['card', 'paypal', 'credit'],
            'now': now()
        })
        return context


    
class CompletePaymentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        method = request.POST.get('method')

        if not request.session.get('cart_pending'):
            messages.error(request, "No hay una compra pendiente.")
            return redirect('cart_view')

        cart = transaction_service.get_or_create_cart_for_user(request.user)
        items = list(cart.items.all())

        invoice = transaction_service.process_checkout(request.user, items)
        transaction_service.complete_payment(request.user, invoice.total, method)

        del request.session['cart_pending']  # Limpiar la bandera
        messages.success(request, "Pago exitoso.")
        return redirect('invoice_success', invoice_id=invoice.id)

class InvoiceSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/invoice_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice_id = self.kwargs.get('invoice_id')
        invoice = invoice_repo.get_invoice_by_id(invoice_id)

        if not invoice or invoice.user != self.request.user:
            raise Http404("Factura no encontrada o acceso denegado.")

        context.update({
            'invoice': invoice
        })
        return context
