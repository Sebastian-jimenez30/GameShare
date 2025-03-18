# apps/transactions/views.py

from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, DetailView
from django.views import View
from django.contrib import messages
from django.contrib.auth import get_user_model

from .models import SharedRental
from .services import TransactionService
from .repositories import (
    RentalRepository, PurchaseRepository, SharedRentalRepository,
    SharedRentalPaymentRepository, CartRepository, CartItemRepository,
    InvoiceRepository, PaymentRepository
)

User = get_user_model()

transaction_service = TransactionService(
    rental_repo=RentalRepository(),
    purchase_repo=PurchaseRepository(),
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

        try:
            transaction_service.add_item_to_cart_by_game_id(request.user.id, game_id, item_type)
            messages.success(request, "Juego añadido correctamente al carrito.")
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('catalog')


class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/cart_view.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = transaction_service.get_or_create_cart_for_user(self.request.user)
        context['cart'] = cart
        context['items'] = cart.cartitem_set.all()
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
            transaction_service.checkout_cart(request.user)
            messages.success(request, "Compra realizada exitosamente.")
        except ValueError as e:
            messages.error(request, str(e))

        return redirect('catalog')


class SharedRentalDetailsView(LoginRequiredMixin, DetailView):
    model = SharedRental
    template_name = 'transactions/shared_rental_details.html'
    context_object_name = 'shared_rental'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shared_rental = self.get_object()

        payments = shared_rental.sharedrentalpayment_set.all()

        context.update({
            'paid_users': payments.filter(status='completed'),
            'pending_users': payments.filter(status='pending'),
            'user_has_paid': payments.filter(user=self.request.user, status='completed').exists(),
        })
        return context
    
class UpdateCartItemTypeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        new_type = request.POST.get('item_type')

        try:
            item = transaction_service.cart_item_repo.get_cart_item_by_id(item_id)
            if not item or item.cart.user != request.user:
                messages.error(request, "Ítem no encontrado o acceso denegado.")
                return redirect('cart_view')

            if new_type in ['rent', 'purchase', 'shared']:
                transaction_service.cart_item_repo.update_cart_item(item_id, {'item_type': new_type})
                transaction_service.update_cart_total(item.cart)
                messages.success(request, "Tipo de ítem actualizado correctamente.")
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
            combined_users = set(item.shared_users.all()).union(new_users)

            if len(combined_users) > 4:
                messages.warning(request, "No puedes compartir con más de 4 usuarios.")
                return redirect('cart_view')

            item.shared_users.set(combined_users)
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

            item.shared_users.remove(user_to_remove)
            item.save()

            messages.success(request, f"Usuario {user_to_remove.username} eliminado del grupo compartido.")
        except Exception as e:
            messages.error(request, str(e))

        return redirect('cart_view')
