from django.db import models
from decimal import Decimal
from apps.users.models import User
from apps.games.models import Game


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('rental', 'Rental'),
        ('shared_rental', 'Shared Rental'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.title()} of {self.game.title} by {self.user.username}"


class Rental(models.Model):
    RENTAL_TYPE_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
    ]

    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='rental_detail')
    rental_type = models.CharField(max_length=10, choices=RENTAL_TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('finished', 'Finished')])

    @property
    def duration(self):
        if self.rental_type == 'hourly':
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() // 3600)
        elif self.rental_type == 'daily':
            delta = self.end_time.date() - self.start_time.date()
            return delta.days
        return 0

    def __str__(self):
        return f"{self.transaction.user.username} rented {self.transaction.game.title}"


class SharedRental(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='shared_rentals')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_shared_rentals')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Shared rental of {self.game.title} by {self.created_by.username}"

    @property
    def is_fully_paid(self):
        return all(payment.status == 'completed' for payment in self.payments.all())


class SharedRentalPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    shared_rental = models.ForeignKey(SharedRental, on_delete=models.CASCADE, related_name='payments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_rental_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    payment_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('shared_rental', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.shared_rental.game.title} - {self.status}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')

    def __str__(self):
        return f"Cart of {self.user.username}"

    # Se eliminará `total_amount` como propiedad aquí si se va a delegar al servicio


class CartItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('purchase', 'Purchase'),
        ('rental', 'Rental'),
        ('shared', 'Shared Rental'),
    ]
    RENTAL_TYPE_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
    ]

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    item_type = models.CharField(max_length=15, choices=ITEM_TYPE_CHOICES)
    quantity = models.PositiveIntegerField(default=1)

    rental_type = models.CharField(max_length=10, choices=RENTAL_TYPE_CHOICES, null=True, blank=True)
    duration = models.PositiveIntegerField(default=1, help_text="Cantidad de horas o días para la renta")

    shared_with = models.ManyToManyField(User, blank=True, related_name='shared_cart_items')

    def __str__(self):
        return f"{self.item_type.title()} - {self.game.title}"

    # Se elimina get_total_price del modelo


class Payment(models.Model):
    METHOD_CHOICES = [
        ('card', 'Card'),
        ('paypal', 'PayPal'),
        ('credit', 'Credit'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} paid {self.amount} ({self.method})"


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='invoice')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pdf_file = models.FileField(upload_to='invoices/')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.id} for {self.user.username}"
