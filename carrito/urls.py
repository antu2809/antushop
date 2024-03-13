from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'carrito'

urlpatterns = [
    path('agregar/<int:producto_id>/<str:producto_model>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('ver/', views.ver_carrito, name='ver_carrito'),
    path('eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
