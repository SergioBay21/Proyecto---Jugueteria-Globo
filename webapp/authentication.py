from django.contrib.auth.backends import BaseBackend
from .models import Usuario

class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            # Buscar el usuario por su email
            user = Usuario.objects.get(email=email)
            # Comparar la contraseña directamente (sin encriptación)
            if password == user.contraseña:
                return user
        except Usuario.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return None
