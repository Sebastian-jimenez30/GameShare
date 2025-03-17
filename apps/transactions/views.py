
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.games.models import Game
from apps.transactions.models import SharedRental, SharedRentalPayment
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView
from django.utils.timezone import now
from datetime import timedelta
from django.contrib import messages
from apps.transactions.utils import create_shared_rental_with_payments
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from apps.transactions.serializers import SharedRentalSerializer
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


from .models import (
    Rental,
    Purchase,
    SharedRental,
    SharedRentalPayment,
    Cart,
    CartItem,
    Invoice,
    Payment
)
from .serializers import (
    RentalSerializer,
    PurchaseSerializer,
    SharedRentalSerializer,
    SharedRentalPaymentSerializer,
    CartSerializer,
    CartItemSerializer,
    InvoiceSerializer,
    PaymentSerializer
)


class RentalViewSet(viewsets.ModelViewSet):
    queryset = Rental.objects.all()
    serializer_class = RentalSerializer


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer


User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class SharedRentalViewSet(viewsets.ModelViewSet):
    queryset = SharedRental.objects.all()
    serializer_class = SharedRentalSerializer

    def create(self, request, *args, **kwargs):
        game_id = request.data.get('game')
        user_ids = request.data.get('users')

        if not game_id or not user_ids:
            return Response(
                {'error': 'Game ID and users list are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            game = Game.objects.get(id=game_id)
        except Game.DoesNotExist:
            return Response({'error': 'Game not found.'}, status=status.HTTP_404_NOT_FOUND)

        invalid_users = [uid for uid in user_ids if not User.objects.filter(id=uid).exists()]
        if invalid_users:
            return Response({'error': f'Invalid user IDs: {invalid_users}'}, status=status.HTTP_400_BAD_REQUEST)

        shared_rental = SharedRental.objects.create(game_id=game_id)

        game = Game.objects.get(id=game_id)
        total_amount = float(game.price)
        amount_per_user = total_amount / len(user_ids)

        for user_id in user_ids:
            SharedRentalPayment.objects.create(
                shared_rental=shared_rental,
                user_id=user_id,
                amount=amount_per_user,
                status='pending'
            )

        shared_rental.users.set(user_ids)

        serializer = self.get_serializer(shared_rental)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='can-download/(?P<user_id>[^/.]+)')
    def can_download(self, request, pk=None, user_id=None):
        shared_rental = self.get_object()
        try:
            payment = shared_rental.sharedrentalpayment_set.get(user_id=user_id)
            is_allowed = shared_rental.is_fully_paid() and payment.status == 'completed'
            return Response({'can_download': is_allowed})
        except SharedRentalPayment.DoesNotExist:
            return Response({'can_download': False})


class SharedRentalPaymentViewSet(viewsets.ModelViewSet):
    queryset = SharedRentalPayment.objects.all()
    serializer_class = SharedRentalPaymentSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def perform_create(self, serializer):
        user = self.request.user

        # Obtener o crear el carrito del usuario
        cart, created = Cart.objects.get_or_create(user=user)

        # Asociar automáticamente el ítem al carrito del usuario
        serializer.save(cart=cart)

        # Opcional: actualizar el total del carrito después de agregar ítem
        cart.update_total()

    def get_queryset(self):
        # Para que el usuario vea solo sus ítems
        return CartItem.objects.filter(cart__user=self.request.user)



class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        game_id = request.POST.get('game_id')
        item_type = request.POST.get('item_type')

        game = get_object_or_404(Game, id=game_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        CartItem.objects.create(cart=cart, game=game, item_type=item_type, quantity=1)
        cart.update_total()

        return redirect('catalog')
    
class CartView(LoginRequiredMixin, TemplateView):
    template_name = 'transactions/cart_view.html'
    login_url = 'login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        context['cart'] = cart
        context['items'] = cart.cartitem_set.all()
        return context
    
class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart = item.cart
        item.delete()
        cart.update_total()
        return redirect('cart_view')

class UpdateCartItemTypeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        new_type = request.POST.get('item_type')

        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        if new_type in ['rent', 'purchase', 'shared']:
            item.item_type = new_type
            item.save()
            item.cart.update_total()

        return redirect('cart_view')

class UpdateCartItemSharedUsersView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        usernames = request.POST.get('usernames', '').split(',')
        usernames = [u.strip() for u in usernames if u.strip()]

        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

        if item.item_type != 'shared':
            messages.error(request, "Este ítem no es de tipo 'shared'.")
            return redirect('cart_view')

        new_users = User.objects.filter(username__in=usernames).exclude(id=request.user.id).distinct()

        # Unir usuarios actuales + nuevos sin duplicados
        current_users = set(item.shared_users.all())
        combined_users = current_users.union(new_users)

        if len(combined_users) > 4:
            messages.warning(request, "No puedes tener más de 4 usuarios para compartir.")
            return redirect('cart_view')

        # Agregar solo los nuevos usuarios (ya que los anteriores ya están)
        for user in new_users:
            item.shared_users.add(user)

        item.save()
        messages.success(request, "Usuarios añadidos correctamente.")
        return redirect('cart_view')

    
class RemoveSharedUserFromCartItemView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        item_id = kwargs.get('item_id')
        user_id = kwargs.get('user_id')

        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        user_to_remove = get_object_or_404(User, id=user_id)

        item.shared_users.remove(user_to_remove)
        item.save()
        messages.success(request, f"Usuario {user_to_remove.username} eliminado del grupo compartido.")
        return redirect('cart_view')



    
class CheckoutCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        items = cart.cartitem_set.all()

        for item in items:
            if item.item_type == 'purchase':
                Purchase.objects.create(user=request.user, game=item.game, date=now())

            elif item.item_type == 'rent':
                Rental.objects.create(
                    user=request.user,
                    game=item.game,
                    start_date=now(),
                    end_date=now() + timedelta(days=7),
                    total_price=item.game.price,
                    status='active'
                )

            elif item.item_type == 'shared':
                shared_users = list(item.shared_users.all())

                # Asegurar que el usuario que hace el checkout también esté incluido
                if request.user not in shared_users:
                    shared_users.append(request.user)

                # ✅ Usa el helper que ya funciona (como desde Swagger)
                create_shared_rental_with_payments(item.game, shared_users)

        # Limpiar carrito
        items.delete()
        cart.total = 0
        cart.save()

        return redirect('catalog')


class SharedRentalDetailsView(LoginRequiredMixin, DetailView):
    model = SharedRental
    template_name = 'transactions/shared_rental_details.html'
    context_object_name = 'shared_rental'

    def get_object(self, queryset=None):
        # Obtiene el objeto SharedRental basado en el id de la URL
        return SharedRental.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shared_rental = self.get_object()

        # Obtener los pagos de los usuarios relacionados con este rental compartido
        shared_rental_payments = SharedRentalPayment.objects.filter(shared_rental=shared_rental)

        # Obtener los usuarios que han pagado y los que no han pagado
        paid_users = shared_rental_payments.filter(status='completed')
        pending_users = shared_rental_payments.filter(status='pending')

        # Identificar si el usuario actual ha pagado
        current_user_payment = shared_rental_payments.filter(user=self.request.user).first()
        user_has_paid = current_user_payment.status == 'completed' if current_user_payment else False

        context.update({
            'paid_users': paid_users,
            'pending_users': pending_users,
            'user_has_paid': user_has_paid,
        })
        return context
