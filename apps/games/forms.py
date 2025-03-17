from django import forms
from .models import Review
from .models import Game

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['title', 'developer', 'year', 'price', 'image', 'category']

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']  # Incluye los campos que quieres mostrar en el formulario

    rating = forms.ChoiceField(choices=Review.RATINGS, widget=forms.RadioSelect)
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe tu comentario...'}))
