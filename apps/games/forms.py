from django import forms
from .models import Game, Category, Review

class GameForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),  # Muestra todas las categorías disponibles
        widget=forms.CheckboxSelectMultiple,  # Casillas de verificación para seleccionar múltiples categorías
        required=False  # Si deseas que las categorías sean opcionales, ponlo en False
    )

    class Meta:
        model = Game
        fields = ['title', 'developer', 'year', 'price', 'image', 'categories']  # Asegúrate de incluir 'categories'
    
    image = forms.ImageField(required=False)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']  # Incluye los campos que quieres mostrar en el formulario

    rating = forms.ChoiceField(choices=Review.RATINGS, widget=forms.RadioSelect)
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe tu comentario...'}))
