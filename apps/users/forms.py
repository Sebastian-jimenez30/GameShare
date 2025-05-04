from django import forms


class UserRegisterForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nombre de usuario")
    email = forms.EmailField(label="Correo electrónico")
    full_name = forms.CharField(max_length=100, label="Nombre completo")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    processor = forms.CharField(max_length=100, label="Procesador")
    ram_gb = forms.IntegerField(label="RAM (GB)")
    graphics_card = forms.CharField(max_length=100, label="Tarjeta gráfica")

    def get_user_data(self):
        return {
            "username": self.cleaned_data["username"],
            "email": self.cleaned_data["email"],
            "full_name": self.cleaned_data["full_name"],
            "password": self.cleaned_data["password"],
            "user_type": "customer",
            "processor": self.cleaned_data["processor"],
            "ram_gb": self.cleaned_data["ram_gb"],
            "graphics_card": self.cleaned_data["graphics_card"]
        }


class UserLoginForm(forms.Form):
    username = forms.CharField(label="Nombre de usuario")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
