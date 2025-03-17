from django import forms

class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    processor = forms.CharField(max_length=100)
    ram_gb = forms.IntegerField()
    graphics_card = forms.CharField(max_length=100)
