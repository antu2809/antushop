from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

class Beat(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_multitrack = models.DecimalField(max_digits=10, decimal_places=2)
    audio_file_multitrack = models.FileField(upload_to='audio/multitrack')
    audio_preview = models.FileField(upload_to='audio/previews', null=True, blank=True)
    image = models.ImageField(upload_to='beats/', blank=True, null=True)
    carrito_items = GenericRelation('carrito.CarritoItem')

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'beats'

class Sample(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price_multitrack = models.DecimalField(max_digits=10, decimal_places=2)
    audio_file_multitrack = models.FileField(upload_to='audio/multitrack')
    audio_preview = models.FileField(upload_to='audio/previews', null=True, blank=True)
    image = models.ImageField(upload_to='beats/', blank=True, null=True)
    carrito_items = GenericRelation('carrito.CarritoItem')

    def __str__(self):
        return self.name
    
    class Meta:
        app_label = 'beats'

class TransaccionPago(models.Model):
    payment_id = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Transacción de Pago {self.payment_id}'

        
        
class Orden(models.Model):
    cliente_nombre = models.CharField(max_length=255)
    cliente_direccion = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=50, default='Pendiente')  # Puedes definir otros estados según tu lógica
    fecha_orden = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Orden - {self.id}'
    