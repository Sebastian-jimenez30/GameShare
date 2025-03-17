from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('customer','Customer'),
        ('admin','Admin'),
    )
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='customer'
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    loyalty_points = models.IntegerField(default=0)

    processor = models.CharField(max_length=100)
    ram_gb = models.IntegerField()
    graphics_card = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Customer: {self.user.username}"

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Admin: {self.user.username}"



