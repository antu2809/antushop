from django.shortcuts import get_object_or_404
from beats.models import Beat, Sample

class Carrito:
    def __init__(self, request):
        self.request = request
        carrito = self.request.session.get('carrito')
        if 'carrito' not in self.request.session:
            carrito = self.request.session['carrito'] = {}
        self.carrito = carrito

    def agregar(self, producto_id, cantidad):
        producto = self.obtener_producto(producto_id)
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {'cantidad': cantidad}
        else:
            self.carrito[producto_id]['cantidad'] += cantidad
        self.guardar_carrito()

    def eliminar(self, producto_id):
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar_carrito()

    def actualizar(self, producto_id, cantidad):
        if cantidad > 0:
            self.carrito[producto_id]['cantidad'] = cantidad
        else:
            self.eliminar(producto_id)
        self.guardar_carrito()

    def limpiar(self):
        self.request.session['carrito'] = {}
        self.guardar_carrito()

    def guardar_carrito(self):
        self.request.session.modified = True

    def obtener_producto(self, producto_id):
        try:
            return Beat.objects.get(pk=producto_id)
        except Beat.DoesNotExist:
            try:
                return Sample.objects.get(pk=producto_id)
            except Sample.DoesNotExist:
                return None

    def __iter__(self):
        for producto_id, item in self.carrito.items():
            producto = self.obtener_producto(producto_id)
            if producto:
                yield {'producto': producto, 'cantidad': item['cantidad']}

    def __len__(self):
        return sum(item['cantidad'] for item in self.carrito.values())

    def get_subtotal(self):
        subtotal = 0
        for item in self:
            subtotal += item['producto'].price_multitrack * item['cantidad']
        return subtotal

    def get_total(self):
        subtotal = self.get_subtotal()
        total = subtotal * 1.16  # IVA del 16%
        return total
