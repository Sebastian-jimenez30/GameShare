# games/tests/test_game_view.py
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Category, Game


class GameCreateViewTestCase(TestCase):
    def setUp(self):
        # Crear un superusuario para poder acceder al formulario
        self.user = get_user_model().objects.create_superuser(
            username='admin', email='admin@example.com', password='password123'
        )
        # Crear categorías de ejemplo
        self.category = Category.objects.create(name="Action")

    def test_game_create_view_redirects_on_success(self):
        # Iniciar sesión como superusuario
        self.client.login(username='admin', password='password123')

        # Datos del formulario
        form_data = {
            'title': 'New Game',
            'developer': 'New Developer',
            'release_year': 2022,
            'purchase_price': '49.99',
            'rental_price_per_hour': '1.50',
            'rental_price_per_day': '5.00',
            'min_cpu': 'Intel i5',
            'min_ram': 8,
            'min_gpu': 'NVIDIA GTX 1060',
            'rec_cpu': 'Intel i7',
            'rec_ram': 16,
            'rec_gpu': 'NVIDIA RTX 2070',
            'categories': [self.category.id],  # Asignar una categoría
            'available': True,
        }

        # Realizar la solicitud POST al formulario
        response = self.client.post(reverse('game_create'), form_data)

        # Verificar que la vista redirige correctamente al catálogo
        self.assertRedirects(response, reverse('catalog'))

        # Verificar que el juego se ha creado correctamente en la base de datos
        game = Game.objects.get(title='New Game')
        self.assertEqual(game.developer, 'New Developer')
        self.assertEqual(game.release_year, 2022)
