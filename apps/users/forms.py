
from django import forms

class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    processor = forms.CharField(max_length=100)
    ram_gb = forms.IntegerField()
    graphics_card = forms.CharField(max_length=100)

    def get_user_data(self):
        return {
            "username": self.cleaned_data["username"],
            "email": self.cleaned_data["email"],
            "name": self.cleaned_data["name"],
            "password": self.cleaned_data["password"],
            "user_type": "customer",
            "customer": {
                "processor": self.cleaned_data["processor"],
                "ram_gb": self.cleaned_data["ram_gb"],
                "graphics_card": self.cleaned_data["graphics_card"],
            }
        }


class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)