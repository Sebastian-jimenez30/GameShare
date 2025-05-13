# games/tests/test_game_form.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from ..models import Game, Category

class GameFormTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username='admin10', email='admin@example.com', password='password123'
        )
        # Crear categorías de ejemplo
        self.category = Category.objects.create(name="Action")

    def test_create_game_form(self):
        # Iniciar sesión como superusuario
        self.client.login(username='admin10', password='password123')

        # Datos del formulario
        form_data = {
            'title': 'Test Game',
            'developer': 'Test Developer',
            'release_year': 2021,
            'purchase_price': Decimal('59.99'),
            'rental_price_per_hour': Decimal('1.99'),
            'rental_price_per_day': Decimal('7.99'),
            'min_cpu': 'Intel i5',
            'min_ram': 8,
            'min_gpu': 'NVIDIA GTX 1050',
            'rec_cpu': 'Intel i7',
            'rec_ram': 16,
            'rec_gpu': 'NVIDIA RTX 2060',
            'categories': [self.category.id],  # Asignar una categoría
            'available': True,
        }

        # Realizar la solicitud POST al formulario
        response = self.client.post(reverse('game_create'), form_data)

        # Verificar que la respuesta es una redirección
        self.assertRedirects(response, reverse('catalog'))

        # Verificar que el juego se creó en la base de datos
        game = Game.objects.get(title='Test Game')
        self.assertEqual(game.developer, 'Test Developer')
        self.assertEqual(game.purchase_price, Decimal('59.99'))
        self.assertEqual(game.rental_price_per_hour, Decimal('1.99'))
        self.assertEqual(game.rental_price_per_day, Decimal('7.99'))
        self.assertEqual(game.requirements.min_processor, 'Intel i5')
        self.assertTrue(game.available)
        self.assertIn(self.category, game.categories.all())
