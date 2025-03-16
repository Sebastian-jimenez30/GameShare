from django.db import models
from apps.users.models import User

class Category(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return self.category_name

class Game(models.Model):
    title = models.CharField(max_length=100)
    developer = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='static/media', null=True, blank=True)

    category = models.ManyToManyField(Category, through='GameCategory')

    def __str__(self):
        return self.title

class GameCategory(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.game.title} - {self.category.name}"

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    def __str__(self):
        return f"Recommendation for {self.user.username}: {self.game.title}"

class Review(models.Model):
    RATINGS = [(i, str(i)) for i in range(1, 6)]  # 1 a 5 estrellas

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATINGS)
    comment = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.game.title} ({self.rating}⭐)"
