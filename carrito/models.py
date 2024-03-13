from django.db import models
from beats.models import Beat
from beats.models import Sample
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from beats.models import CustomUser
from django.contrib.auth import get_user_model


class CarritoItem(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField(default=1, null=True)
    producto = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f'{self.producto.name} en el carrito de {self.user.username}'


