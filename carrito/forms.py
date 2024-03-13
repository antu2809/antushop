from carrito.models import CarritoItem
from django import forms

class CarritoItemForm(forms.ModelForm):
    class Meta:
        model = CarritoItem
        fields = []  # Sin campos necesarios, no se necesita elegir la cantidad
