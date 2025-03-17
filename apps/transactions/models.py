from django.db import models
from decimal import Decimal
from apps.users.models import User
from apps.games.models import Game


class Rental(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('finished', 'Finished'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f'Rental of {self.game} by {self.user.username}'


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Purchase of {self.game} by {self.user.username}'


class SharedRental(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, through='SharedRentalPayment')

    def __str__(self):
        return f'Shared rental: {self.game}'

    def is_fully_paid(self):
        return all(payment.status == 'completed' for payment in self.sharedrentalpayment_set.all())

    def split_amount_per_user(self, total_amount):
        user_count = self.sharedrentalpayment_set.count()
        return total_amount / user_count if user_count else Decimal('0.00')


class SharedRentalPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]
    shared_rental = models.ForeignKey(SharedRental, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    payment_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.shared_rental.game} - {self.status}'


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Game, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'Cart of {self.user.username}'


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    purchase_transaction = models.ForeignKey(Purchase, null=True, blank=True, on_delete=models.SET_NULL)
    rental_transaction = models.ForeignKey(Rental, null=True, blank=True, on_delete=models.SET_NULL)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='invoices/')

    def __str__(self):
        return f'Invoice #{self.id} for {self.user.username}'


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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment of {self.amount} by {self.user.username}'
