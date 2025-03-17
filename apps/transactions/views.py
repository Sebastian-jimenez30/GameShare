
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.games.models import Game
from django.contrib.auth import get_user_model

from .models import (
    Rental,
    Purchase,
    SharedRental,
    SharedRentalPayment,
    Cart,
    Invoice,
    Payment
)
from .serializers import (
    RentalSerializer,
    PurchaseSerializer,
    SharedRentalSerializer,
    SharedRentalPaymentSerializer,
    CartSerializer,
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


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
