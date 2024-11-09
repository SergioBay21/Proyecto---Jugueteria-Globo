from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from .models import Cuenta
import re

class CheckAccessCodeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
         # Permitimos el acceso a archivos estáticos (incluyendo imágenes)
        if re.match(r'^/static/', request.path) or re.match(r'^/media/', request.path):
            return self.get_response(request)
        allowed_urls_without_code = [
            reverse('send_code'), reverse('validate_code'), reverse('login'),reverse('logout'),reverse('chatbot'),reverse('chatbot_responder'),reverse('productos-compra'),
            reverse('carrito'),reverse('realizar_venta'),
        ]
        allowed_patterns_without_code = [
            r'^/agregar_al_carrito/\d+/$',  
            r'^/eliminar_producto_carrito/\d+/$',
            r'^/productos/eliminar/\d+/$', 
            r'^/productos/editar/\d+/$', # Asegúrate de que esta ruta esté incluida
        ]
        current_path = request.path
        code_validated = request.session.get('code_validated', False)
        two_step_verified = request.session.get('two_step_verified', False)
        user_id = request.session.get('user_id')

        if current_path in allowed_urls_without_code:
            return self.get_response(request)
        if current_path in allowed_urls_without_code or any(re.match(pattern, current_path) for pattern in allowed_patterns_without_code):
            return self.get_response(request)

        if not user_id:
            return redirect('login') if current_path != reverse('login') else self.get_response(request)

        if not code_validated:
            return redirect('send_code') if current_path != reverse('send_code') else self.get_response(request)

        if not two_step_verified:
            if current_path != reverse('two_step_auth'):
                return redirect('two_step_auth')
            return self.get_response(request)

        try:
            cuenta = Cuenta.objects.get(id_usuario=user_id)
            tipo_cuenta = int(cuenta.tipo_cuenta)
        except (Cuenta.DoesNotExist, ValueError, TypeError):
            tipo_cuenta = None

        rutas_por_tipo = {
            1: [reverse('shop'),reverse('chatbot'),reverse('chatbot_responder'),reverse('agregar_al_carrito',args=[0])],
            2: [reverse('shop'), reverse('chatbot'),reverse('chatbot_responder'),reverse('agregar_al_carrito',args=[0])],
            3: [
                reverse('shop'), reverse('admin'), reverse('listar_hijos'),reverse('chatbot'),reverse('chatbot_responder'),
                reverse('agregar_hijo'), reverse('editar_hijo', args=[0]),
                reverse('eliminar_hijo', args=[0]), reverse('agregar_padre'),
                reverse('editar_padre', args=[0]), reverse('productos'),
                reverse('agregar_producto'), reverse('editar_producto', args=[0]),
                reverse('eliminar_producto', args=[0])
            ]
        }

        rutas_permitidas = rutas_por_tipo.get(tipo_cuenta, [])

        if current_path not in rutas_permitidas:
            return redirect('shop') if tipo_cuenta in [1, 2] else redirect('admin')

        return self.get_response(request)
