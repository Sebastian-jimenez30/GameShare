from django.db import models
from apps.users.models import User
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class GameRequirements(models.Model):
    # Requerimientos mínimos
    min_processor = models.CharField(max_length=100)
    min_ram_gb = models.PositiveIntegerField()
    min_gpu = models.CharField(max_length=100)

    # Requerimientos recomendados
    rec_processor = models.CharField(max_length=100, blank=True)
    rec_ram_gb = models.PositiveIntegerField(null=True, blank=True)
    rec_gpu = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Reqs (Min: {self.min_processor}/{self.min_ram_gb}GB/{self.min_gpu})"


class Game(models.Model):
    title = models.CharField(max_length=100)
    developer = models.CharField(max_length=100)
    release_year = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=8, decimal_places=2)
    rental_price_per_hour = models.DecimalField(max_digits=6, decimal_places=2)
    rental_price_per_day = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='static/media', null=True, blank=True)
    available = models.BooleanField(default=True)

    requirements = models.OneToOneField(GameRequirements, on_delete=models.CASCADE, related_name='game')

    categories = models.ManyToManyField(Category, through='GameCategory', related_name='games')

    def get_absolute_url(self):
        return reverse('game_detail', args=[str(self.id)])

    def __str__(self):
        return self.title

    def check_availability(self):
        return self.available
    


class GameCategory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('game', 'category')

    def __str__(self):
        return f"{self.game.title} - {self.category.name}"


class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='recommended_to')
    reason = models.TextField()

    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.game.title}"


class Review(models.Model):
    RATINGS = [(i, f"{i} ⭐") for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATINGS)
    comment = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f"{self.user.username} → {self.game.title} ({self.rating}⭐)"
