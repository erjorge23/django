from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# --- FORMULARIO 1: EL BUSCADOR (Para buscar productos) ---
class BusquedaProductoForm(forms.Form):
    nombre_producto = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '¿Qué producto buscas?',
            'autofocus': True
        })
    )

# --- FORMULARIO 2: EL REGISTRO (Para crear usuarios nuevos) ---
class RegistroForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email'] # Pedimos Usuario y Email
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
        }
        help_texts = {
            'username': None, # Esto borra el texto de ayuda molesto de Django
        }

    # Esto añade el estilo de Bootstrap a las casillas automáticamente
    def __init__(self, *args, **kwargs):
        super(RegistroForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})