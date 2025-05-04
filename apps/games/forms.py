from django import forms
from .models import Game, Category, Review



from django import forms
from .models import Game, Category, Review

class GameForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    # Campos para requisitos mínimos
    min_cpu = forms.CharField(label="CPU Mínima", required=False)
    min_ram = forms.IntegerField(label="RAM Mínima (GB)", required=False)
    min_gpu = forms.CharField(label="GPU Mínima", required=False)

    # Campos para requisitos recomendados
    rec_cpu = forms.CharField(label="CPU Recomendada", required=False)
    rec_ram = forms.IntegerField(label="RAM Recomendada (GB)", required=False)
    rec_gpu = forms.CharField(label="GPU Recomendada", required=False)

    class Meta:
        model = Game
        fields = [
            'title',
            'developer',
            'release_year',
            'purchase_price',
            'rental_price_per_hour',
            'rental_price_per_day',
            'image',
            'available',
            'categories',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Precargar los campos desde el objeto de requisitos si existe
        if self.instance and hasattr(self.instance, "requirements"):
            req = self.instance.requirements
            self.fields['min_cpu'].initial = req.min_processor
            self.fields['min_ram'].initial = req.min_ram_gb
            self.fields['min_gpu'].initial = req.min_gpu
            self.fields['rec_cpu'].initial = req.rec_processor
            self.fields['rec_ram'].initial = req.rec_ram_gb
            self.fields['rec_gpu'].initial = req.rec_gpu

    def get_requirements_data(self):
        return {
            'min_processor': self.cleaned_data.get('min_cpu'),
            'min_ram_gb': self.cleaned_data.get('min_ram'),
            'min_gpu': self.cleaned_data.get('min_gpu'),
            'rec_processor': self.cleaned_data.get('rec_cpu'),
            'rec_ram_gb': self.cleaned_data.get('rec_ram'),
            'rec_gpu': self.cleaned_data.get('rec_gpu'),
        }

class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=Review.RATINGS,
        widget=forms.RadioSelect,
        label="Calificación"
    )
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe tu comentario...'}),
        required=False,
        label="Comentario"
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
