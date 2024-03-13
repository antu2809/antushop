"""
URL configuration for antushop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from beats import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.tienda, name='tienda'),
    path('iniciar_sesion/', views.iniciar_sesion, name='iniciar_sesion'),
    path('cambiar_contrasena/', views.cambiar_contrasena, name='cambiar_contrasena'),
    path('verificar-cambio-contrasena/<str:uidb64>/<str:token>/', views.verificar_cambio_contrasena, name='verificar_cambio_contrasena'),
    path('confirmacion_correo_enviado/', views.confirmacion_correo_enviado, name='confirmacion_correo_enviado'),
    path('contrasena-cambiada-exitosamente/', views.contrasena_cambiada_exitosamente, name='contrasena_cambiada_exitosamente'),
    path('registro/', views.registro, name='registro'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('carrito/', include('carrito.urls')),  
    path('iniciar_pago/', views.iniciar_pago, name='iniciar_pago'),
    path('success/', views.success, name='success'),
    path('failure/', views.failure, name='failure'),
    path('pending/', views.pending, name='pending'),
    path('webhook/', views.webhook, name='webhook'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
