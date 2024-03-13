from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

from .carrito import Carrito

from .forms import CarritoItemForm

from .models import CarritoItem
from beats.models import Beat, Sample


@login_required
def agregar_al_carrito(request, producto_id, producto_model):
    producto_model_class = Beat if producto_model == 'beat' else Sample
    producto = get_object_or_404(producto_model_class, id=producto_id)

    # Obtener el ContentType del modelo del producto
    content_type = ContentType.objects.get_for_model(producto_model_class)

    # Crear un nuevo CarritoItem y asociarlo con el usuario y el producto
    carrito_item, created = CarritoItem.objects.get_or_create(
        user=request.user,
        content_type=content_type,
        object_id=producto_id,
        cantidad=1
    )

    if created:
        print(f'Producto agregado al carrito - ID: {producto.id}, Nombre: {producto.name}')

        print(f'Producto "{producto.name}" creado y agregado al carrito')
    else:
        print(f'Producto "{producto.name}" ya estaba en el carrito')

    return redirect('tienda')

def ver_carrito(request):
    carrito = CarritoItem.objects.filter(user=request.user)
    for item in carrito:
        print(f'ID del producto en el carrito: {item.producto.id}, Nombre del producto en el carrito: {item.producto.name}')

    
    total = sum(item.producto.price_multitrack * item.cantidad for item in carrito)
    print(f'Elementos del carrito para el usuario {request.user.username}: {carrito}')
    print(f'Total del carrito: ${total}')
    
    # Extraer los datos del pagador si están disponibles en la sesión
    pagador = request.session.get('pagador', {})

    context = {
        'carrito': carrito,
        'total': total,
        'pagador': pagador,
        'eliminar_del_carrito': eliminar_del_carrito,
    }
    return render(request, 'carrito/ver_carrito.html', context)

def eliminar_del_carrito(request, item_id):
    print(f'Item ID recibido en eliminar_del_carrito: {item_id}')
    carrito_item = get_object_or_404(CarritoItem, id=item_id, user=request.user)
    carrito_item.delete()
    
    # Obtener la lista actualizada de elementos del carrito después de eliminar el elemento
    carrito = CarritoItem.objects.filter(user=request.user)
    total = sum(item.producto.price_multitrack * item.cantidad for item in carrito)
    
    context = {
        'carrito': carrito,
        'total': total,
    }
    return render(request, 'carrito/ver_carrito.html', context)