from decimal import Decimal, InvalidOperation
from apps.transactions.models import SharedRental, SharedRentalPayment
from django.contrib.auth import get_user_model

User = get_user_model()

def create_shared_rental_with_payments(game, users):
    if not users:
        raise ValueError("La lista de usuarios no puede estar vacía.")
    if not game.price:
        raise ValueError("El juego no tiene precio definido.")

    try:
        total_amount = Decimal(game.price)
    except (TypeError, InvalidOperation):
        raise ValueError("El precio del juego no es válido.")

    amount_per_user = total_amount / Decimal(len(users))

    shared_rental = SharedRental.objects.create(game=game)

    for user in users:
        SharedRentalPayment.objects.create(
            shared_rental=shared_rental,
            user=user,
            amount=amount_per_user,
            status='pending'
        )

    return shared_rental
