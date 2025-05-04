from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )

    username = models.CharField(max_length=150, unique=True)  # ✅ nuevo campo
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    loyalty_points = models.PositiveIntegerField(default=0)

    # Hardware para recomendaciones
    processor = models.CharField(max_length=100, blank=True)
    ram_gb = models.PositiveIntegerField(null=True, blank=True)
    graphics_card = models.CharField(max_length=100, blank=True)

    # Campos requeridos por Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'  # Usamos el email para login
    REQUIRED_FIELDS = ['email', 'full_name']  # ✅ username ahora requerido para superusuarios

    def __str__(self):
        return f"{self.username} ({self.email})"

    @property
    def is_customer(self):
        return self.user_type == 'customer'

    @property
    def is_admin_user(self):
        return self.user_type == 'admin'
