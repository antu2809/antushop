from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import requests
from django.shortcuts import redirect
import json
import logging
from django.core.mail import send_mail
from .forms import CustomUserCreationForm
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

from .models import Beat, Sample, TransaccionPago, CustomUser
from carrito.carrito import Carrito
from carrito.models import CarritoItem

from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.utils.encoding import force_bytes
from django.urls import reverse


def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('tienda')  # Redirige a la tienda después de iniciar sesión
    else:
        form = AuthenticationForm()
    return render(request, 'iniciar_sesion.html', {'form': form})

def registro(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tienda')  # Redirige a la tienda después de registrarse
    else:
        form = CustomUserCreationForm()
    return render(request, 'registro.html', {'form': form})


def cerrar_sesion(request):
    logout(request)
    return redirect('tienda')  # Redirige a la tienda después de cerrar sesión

from django.utils.http import urlsafe_base64_encode

def cambiar_contrasena(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user:
                # Generar token para el usuario
                token = default_token_generator.make_token(user)

                # Construir URL de verificación
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                current_site = request.build_absolute_uri('/')[:-1]  # Obtener la URL base (localhost)
                token_url = reverse('verificar_cambio_contrasena', kwargs={'uidb64': uidb64, 'token': token})
                token_url = f'{current_site}{token_url}'  # Agregar la URL base a la URL de verificación

                # Construir el cuerpo del correo electrónico
                email_subject = 'Verificación de Cambio de Contraseña'
                email_message = render_to_string('email/verificacion_cambio_contrasena.html', {
                    'user': user,
                    'token_url': token_url,
                })

                # Enviar correo electrónico de verificación
                send_mail(email_subject, email_message, 'franciscoantualmonacidcammarata@gmail.com', [email])

                # Redirigir a la página de confirmación de correo electrónico
                return redirect('confirmacion_correo_enviado')
            else:
                messages.error(request, 'No se encontró ningún usuario con este correo electrónico.')
    else:
        form = CustomPasswordResetForm()
    return render(request, 'cambiar_contrasena.html', {'form': form})

from django.utils.http import urlsafe_base64_decode

def verificar_cambio_contrasena(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = CustomSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return redirect('contrasena_cambiada_exitosamente')
        else:
            form = CustomSetPasswordForm(user)
        return render(request, 'verificar_cambio_contrasena.html', {'form': form})
    else:
        return HttpResponse('El enlace de verificación es inválido o ha expirado.')

def confirmacion_correo_enviado(request):
    return render(request, 'email/confirmacion_correo_enviado.html')

def contrasena_cambiada_exitosamente(request):
    return render(request, 'contrasena_cambiada_exitosamente.html')

def tienda(request):
    beats = Beat.objects.all()
    samples = Sample.objects.all()
    carrito = Carrito(request)  # Obtener el carrito del usuario
    total = carrito.get_total()  # Obtener el total del carrito

    context = {
        'beats': beats,
        'samples': samples,
        'producto_model': 'beat',
        'carrito_items': carrito,  # Pasar el carrito directamente al contexto
        'total': total,
    }
    return render(request, 'tienda.html', context)

@login_required
def iniciar_pago(request):
    if request.method == 'POST':
        # Realizar solicitud a MercadoPago
        access_token = settings.MERCADOPAGO_ACCESS_TOKEN
        # Imprimir todos los datos del formulario POST para asegurarte de que no falte ninguno
        print("Datos del formulario POST:", request.POST.dict())
        # Obtener los datos del pagador y los productos del formulario POST
        pagador_name = request.POST.get('name')
        pagador_surname = request.POST.get('surname')
        pagador_email = request.POST.get('email')
        pagador_area_code = request.POST.get('area_code')
        pagador_phone_number = request.POST.get('phone_number')
        pagador_street_name = request.POST.get('street_name')
        pagador_street_number = request.POST.get('street_number')
        pagador_zip_code = request.POST.get('zip_code')
        productos_ids = request.POST.getlist('productos[]')  # Obtener la lista de IDs de productos
        cantidades = request.POST.getlist('cantidades[]')     # Obtener la lista de cantidades

        # Imprimir los valores de los campos del pagador para depuración
        print("Nombre:", pagador_name)
        print("Apellido:", pagador_surname)
        print("Email:", pagador_email)
        print("Código de Área:", pagador_area_code)
        print("Número de Teléfono:", pagador_phone_number)
        print("Calle:", pagador_street_name, pagador_street_number)
        print("Código Postal:", pagador_zip_code)

        # Verificar si todos los campos del formulario están presentes
        if not all([pagador_name, pagador_surname, pagador_email, pagador_area_code, pagador_phone_number, pagador_street_name, pagador_street_number, pagador_zip_code]):
            # Si falta algún campo, imprimir un mensaje de depuración
            print("Faltan campos obligatorios en el formulario")
            return JsonResponse({'error': 'Faltan campos obligatorios en el formulario'})

        # Procesar el carrito
        carrito = CarritoItem.objects.filter(user=request.user)
        productos = []

        for item in carrito:
            producto = item.producto
            productos.append({
                'id': str(producto.id),
                'title': producto.name,
                'description': producto.description,
                'quantity': item.cantidad,
                'currency_id': 'USD',
                'unit_price': float(producto.price_multitrack),
                'picture_url': producto.image.url,
            })

        # Crear datos de preferencia de MercadoPago
        preference_data = {
            'items': productos,
            'payer': {
                'name': pagador_name,
                'surname': pagador_surname,
                'email': pagador_email,
                'phone': {
                    'area_code': pagador_area_code,
                    'number': pagador_phone_number,
                },
                'address': {
                    'street_name': pagador_street_name,
                    'street_number': pagador_street_number,
                    'zip_code': pagador_zip_code,
                },
            },
            'back_urls': {
                'success': '/success/',
                'failure': '/failure/',
                'pending': '/pending/',
            },
            'notification_url': '/webhook/',
            'external_reference': 'antualmonacid@gmail.com',
            'payment_methods': {
                'installments': 6,
            },
        }

        print("Datos de preferencia de MercadoPago:", preference_data)
        integrator_id = 'dev_e4e7ce754cb611ee96292e7ca281d093'
        url = 'https://api.mercadopago.com/checkout/preferences'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Integrator-Id': integrator_id,
            'Referer': '',  # Cambia esto a tu dominio real
        }

        response = requests.post(url, data=json.dumps(preference_data), headers=headers)
        print("Respuesta de Mercado Pago:", response.text)

        # Manejar la respuesta de MercadoPago
        if response.status_code == 201:
            try:
                preference = response.json()
                init_point = preference.get('init_point')

                if init_point:
                    print("init_point:", init_point)
                    #return JsonResponse({'init_point': init_point, 'html_content': ''})
                    return HttpResponseRedirect(init_point)
                    # Devolver la respuesta JSON con el init_point
                    #return JsonResponse({'init_point': init_point})
                else:
                    return JsonResponse({'error': 'No se encontró la URL de inicio de pago'})
            except json.JSONDecodeError:
                return JsonResponse({'error': 'La respuesta no es un JSON válido'})
        else:
            return JsonResponse({'error': 'Error al crear la preferencia de pago'})

    return JsonResponse({'error': 'No se ha enviado una solicitud POST.'})


def success(request):
    # Procesa la página de éxito y muestra información del pago
    # Consulta los parámetros en la URL y muestra la información relevante

    # Consulta los parámetros que se envían en la Query String cuando Mercado Pago redirige a las URLs de retorno configuradas en la URL
    collection_id = request.GET.get('collection_id')
    collection_status = request.GET.get('collection_status')
    external_reference = request.GET.get('external_reference')
    payment_method_id = request.GET.get('payment_method_id')
    payment_type = request.GET.get('payment_type')
    preference_id = request.GET.get('preference_id')
    site_id = request.GET.get('site_id')
    processing_mode = request.GET.get('processing_mode')
    merchant_account_id = request.GET.get('merchant_account_id')

    # Procesa la información y muestra la página de fallo
    context = {
        'collection_id': collection_id,
        'collection_status': collection_status,
        'external_reference': external_reference,
        'payment_method_id': payment_method_id,
        'payment_type': payment_type,
        'preference_id': preference_id,
        'site_id': site_id,
        'processing_mode': processing_mode,
        'merchant_account_id': merchant_account_id,
    }
    
    # Llama a send_email_success si el pago fue exitoso
    if collection_status == 'approved':
        pagador_email = request.POST.get('email')  # Obtener el correo electrónico del comprador
        productos = obtener_productos_comprados(request)  # Obtener la lista de productos comprados
        send_email_success(pagador_email, productos)

    return render(request, 'success.html', context)

def obtener_productos_comprados(request):
    productos = []
    carrito = CarritoItem.objects.filter(user=request.user)
    
    for item in carrito:
        producto = item.producto
        productos.append({
            'title': producto.name,
            'unit_price': float(producto.price_multitrack),
            'quantity': item.cantidad,
        })

    return productos

def send_email_success(email, productos):
    subject = 'Compra Exitosa en Antu Shop'
    message = 'Gracias por tu compra. Has adquirido los siguientes productos:\n\n'
    
    for producto in productos:
        message += f"- {producto['title']} - ${producto['unit_price']} ({producto['quantity']} unidades)\n"
    
    send_mail(subject, message, 'franciscoantualmonacid@gmail.com', [email])

def failure(request):
    # Procesa la página de fallo y muestra información del pago rechazado
    # Consulta los parámetros en la URL y muestra la información relevante

    # Consulta los parámetros que se envían en la Query String cuando Mercado Pago redirige a las URLs de retorno configuradas en la URL
    collection_id = request.GET.get('collection_id')
    collection_status = request.GET.get('collection_status')
    external_reference = request.GET.get('external_reference')
    payment_method_id = request.GET.get('payment_method_id')
    payment_type = request.GET.get('payment_type')
    preference_id = request.GET.get('preference_id')
    site_id = request.GET.get('site_id')
    processing_mode = request.GET.get('processing_mode')
    merchant_account_id = request.GET.get('merchant_account_id')

    # Procesa la información y muestra la página de fallo
    context = {
        'collection_id': collection_id,
        'collection_status': collection_status,
        'external_reference': external_reference,
        'payment_method_id': payment_method_id,
        'payment_type': payment_type,
        'preference_id': preference_id,
        'site_id': site_id,
        'processing_mode': processing_mode,
        'merchant_account_id': merchant_account_id,
    }

    return render(request, 'failure.html', context)

def pending(request):
    # Procesa la página de pago pendiente y muestra información relevante
    # Consulta los parámetros en la URL y muestra la información relevante

    # Consulta los parámetros que se envían en la Query String cuando Mercado Pago redirige a las URLs de retorno configuradas en la URL
    collection_id = request.GET.get('collection_id')
    collection_status = request.GET.get('collection_status')
    external_reference = request.GET.get('external_reference')
    payment_method_id = request.GET.get('payment_method_id')
    payment_type = request.GET.get('payment_type')
    preference_id = request.GET.get('preference_id')
    site_id = request.GET.get('site_id')
    processing_mode = request.GET.get('processing_mode')
    merchant_account_id = request.GET.get('merchant_account_id')

    # Procesa la información y muestra la página de fallo
    context = {
        'collection_id': collection_id,
        'collection_status': collection_status,
        'external_reference': external_reference,
        'payment_method_id': payment_method_id,
        'payment_type': payment_type,
        'preference_id': preference_id,
        'site_id': site_id,
        'processing_mode': processing_mode,
        'merchant_account_id': merchant_account_id,
    }

    return render(request, 'pending.html', context)

def webhook(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            logging.error('Error al decodificar JSON de la notificación')
            return HttpResponse(status=400)

        # Inicializa payment_id como None
        payment_id = None

        # Verifica si la notificación es de tipo "payment" o "test.created"
        if 'type' in data:
            if data['type'] == 'payment':
                payment_data = data.get('data', {})
                payment_id = payment_data.get('id')
                if payment_id:
                    # Guardar los detalles del pago base de datos
                    transaccion = TransaccionPago(payment_id=payment_id)
                    transaccion.save()
                    logging.info(f'Pago exitoso: Payment ID {payment_id}')

            # Crea un contexto que incluya el Payment ID para tu plantilla
            context = {'payment_id': payment_id}

            if data['type'] == 'test.created':
                request_id = data.get('id')
                api_version = data.get('api_version')
                application_id = data.get('application_id')
                date_created = data.get('date_created')
                user_id = data.get('user_id')
                notification_type = data.get('type')

                context.update({
                    'request_id': request_id,
                    'api_version': api_version,
                    'application_id': application_id,
                    'date_created': date_created,
                    'user_id': user_id,
                    'type': notification_type,
                })

                logging.info(f'Notificación de tipo "test.created" recibida')

        else:
            # Si la notificación no coincide con ningún tipo conocido, devuelve un error
            logging.warning('Notificación de tipo desconocido')
            return HttpResponse(status=400)

        # Renderiza la plantilla 'webhook.html' con el contexto
        return render(request, 'webhook.html', context)

    # Si la solicitud no es POST, devuelve un error 405
    return HttpResponse(status=405)