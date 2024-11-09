
from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .authentication import EmailAuthBackend
from .models import Usuario, Cuenta, CodAuth, DetallePadreHijo, Producto, Venta, DetalleVenta, Carrito, DetalleCarrito, PreguntaRespuesta
import random
import string

# Create your views here.

from django.conf import settings

# Create your views here.
def shop(request):
    productos = Producto.objects.all()  # Obtener todos los productos
    return render(request, 'shop.html', {'productos': productos})
def admin(request):
    return render(request, 'index-admin.html')
def agregar_padre(request):
    # Filtrar cuentas donde id_cuenta = 1
    cuentas = Cuenta.objects.filter(tipo_cuenta=1)  # Muestra todas las cuentas

    if request.method == 'POST':
        # Agregar padre
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        contraseña = request.POST.get('contraseña')

        if nombre and email and contraseña:
            # Guardar nuevo usuario
            usuario = Usuario(nombre=nombre, email=email, contraseña=contraseña)  # Asegúrate de hashear la contraseña
            usuario.save()

            # Guardar cuenta del padre (tipo_cuenta = 'Padre')
            cuenta = Cuenta(id_usuario=usuario, tipo_cuenta=1)  # Usa el objeto usuario
            cuenta.save()

            messages.success(request, 'Padre agregado exitosamente.')
            return redirect('agregar_padre')  # Asegúrate de que esta URL esté bien definida

    # Si no es POST, solo mostrar la lista de cuentas
    context = {
        'cuentas': cuentas,
    }
    return render(request, 'admin-padres.html', context)
def editar_padre(request, id_cuenta):
    cuenta = get_object_or_404(Cuenta, id_cuenta=id_cuenta)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')

        if nombre and email:
            usuario = Usuario.objects.get(id_usuario=cuenta.id_usuario.id_usuario)
            usuario.nombre = nombre
            usuario.email = email
            usuario.save()

            messages.success(request, 'Información de padre actualizada exitosamente.')
            return redirect('agregar_padre')  # Cambia esto por el nombre de tu URL correspondiente

    context = {
        'cuenta': cuenta,
    }
    return render(request, 'editar_padre.html', context)

def listar_hijos(request):
    # Obtener todos los padres disponibles
    padres = Cuenta.objects.filter(tipo_cuenta=1)

    # Obtener todos los hijos con relación a sus padres
    hijos_con_padres = DetallePadreHijo.objects.select_related('id_cuenta_hijo', 'id_cuenta_padre').all()

    return render(request, 'admin-hijos.html', {
        'padres': padres,
        'hijos_con_padres': hijos_con_padres,
    })



def agregar_hijo(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        email = request.POST['email']
        contraseña = request.POST['contraseña']
        padre_id = request.POST['padre']
        
        # Crear usuario
        nuevo_usuario = Usuario.objects.create(nombre=nombre, email=email, contraseña=contraseña)
        
        # Crear cuenta para el hijo
        nueva_cuenta = Cuenta.objects.create(id_usuario=nuevo_usuario, tipo_cuenta=2)
        
        # Asignar al padre
        DetallePadreHijo.objects.create(id_cuenta_padre_id=padre_id, id_cuenta_hijo=nueva_cuenta)

        return redirect('listar_hijos')

def editar_hijo(request, id_cuenta):
    hijo = get_object_or_404(Cuenta, id_cuenta=id_cuenta)

    if request.method == 'POST':
        hijo.id_usuario.nombre = request.POST['nombre']
        hijo.id_usuario.email = request.POST['email']
        hijo.id_usuario.contraseña = (request.POST['contraseña'])  # Si quieres cambiar la contraseña
        hijo.id_usuario.save()

        return redirect('listar_hijos')
    
    return render(request, 'admin-hijos.html', {'hijo': hijo})

def eliminar_hijo(request, id_cuenta):
    hijo = get_object_or_404(Cuenta, id_cuenta=id_cuenta)
    
    # Eliminar relación en detalle_padre_hijo
    DetallePadreHijo.objects.filter(id_cuenta_hijo=hijo).delete()
    # Eliminar la cuenta del hijo
    hijo.delete()

    return redirect('listar_hijos')

def productos_admin(request):
    return render(request, 'admin-productos.html')

# Se definen los métodos
def send_code(request):
    if request.method == 'POST':
        # Generar el código de 8 caracteres
        code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        # Actualizar el código en la base de datos (id_cod_acceso = 1)
        with connection.cursor() as cursor:
            cursor.execute("UPDATE cod_acceso SET cod_acceso = %s WHERE id_cod_acceso = 1", [code])

        # Enviar el código al correo electrónico
        send_mail(
            'Código de Acceso',
            f'Tu código de acceso es: {code}',
            'sergiobaye@gmail.com',
            ['sbaye@miumg.edu.gt'],
            fail_silently=False,
        )

        # Mostrar mensaje de éxito
        messages.success(request, 'El código de acceso ha sido enviado a tu correo.')

        # Redirigir a la página de validación
        return redirect('validate_code')  # Cambia 'validate_code' por el nombre que hayas asignado a tu URL de validación

    return render(request, 'send_code.html')

def validate_code(request):
    if request.method == 'POST':
        input_code = request.POST.get('access_code')

        if input_code:
            with connection.cursor() as cursor:
                cursor.execute("SELECT cod_acceso FROM cod_acceso WHERE id_cod_acceso = 1")
                row = cursor.fetchone()

            if row and row[0] == input_code:
                # Establecer que el código fue validado
                request.session['code_validated'] = True
                return redirect('login')
            else:
                messages.error(request, 'El código de acceso no es válido.')
        else:
            messages.error(request, 'Por favor, ingrese un código.')

    return render(request, 'validate_code.html')



def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        backend = EmailAuthBackend()
        user = backend.authenticate(request, email=email, password=password)

        if user is not None:
            request.session['user_id'] = user.id_usuario  # Guardar el ID en la sesión
            request.session['email'] = user.email
            return redirect('two_step_auth')
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'login.html')


def two_step_auth_view(request):
    if request.method == 'POST':
        code_entered = request.POST.get('code')

        try:
            correct_code = CodAuth.objects.get(id_cod=1).cod_auth
        except CodAuth.DoesNotExist:
            messages.error(request, 'Error en la base de datos.')
            return redirect('login')

        if code_entered == correct_code:
            request.session['two_step_verified'] = True  # Establecer que la verificación fue exitosa

            # Obtener el tipo de cuenta del usuario y redirigir
            user_id = request.session.get('user_id')
            cuenta = Cuenta.objects.get(id_usuario=user_id)
            
            if cuenta.tipo_cuenta == 1 or cuenta.tipo_cuenta == 2:
                return redirect('shop')  # Redirige a shop para padres e hijos
            elif cuenta.tipo_cuenta == 3:
                return redirect('admin')  # Redirige a admin para administradores
        else:
            messages.error(request, 'Código incorrecto.')

    return render(request, 'two_step_auth.html')

def listar_productos_admin(request):
    productos = Producto.objects.all()  # Obtener todos los productos
    return render(request, 'admin-productos.html', {'productos': productos})

def agregar_producto(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        existencia = request.POST['existencia']
        precio = request.POST['precio']
        categoria = request.POST['categoria']
        imagen = request.FILES['imagen'] if 'imagen' in request.FILES else None

        # Guardar la imagen en la carpeta especificada
        if imagen:
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)  # Guardar en 'static/images/'
            filename = fs.save(imagen.name, imagen)
            uploaded_file_url = fs.url(filename)
        else:
            uploaded_file_url = None

        # Crear el producto en la base de datos
        nuevo_producto = Producto(
            nombre=nombre,
            existencia=existencia,
            precio=precio,
            categoria=categoria,
            imagen=uploaded_file_url
        )
        nuevo_producto.save()

        return redirect('productos')

    return render(request, 'admin-productos.html')
def editar_producto(request, id_producto):
    producto = get_object_or_404(Producto, id_producto=id_producto)

    if request.method == 'POST':
        producto.nombre = request.POST['nombre']
        producto.existencia = request.POST['existencia']
        producto.precio = request.POST['precio']
        producto.categoria = request.POST['categoria']
        
        if 'imagen' in request.FILES:
            imagen = request.FILES['imagen']
            fs = FileSystemStorage(location=settings.MEDIA_ROOT)
            filename = fs.save(imagen.name, imagen)
            producto.imagen = filename

        producto.save()
        return redirect('productos')

# Eliminar producto
def eliminar_producto(request, id_producto):
    producto = get_object_or_404(Producto, id_producto=id_producto)
    producto.delete()
    return redirect('productos')

def logout_view(request):
    # Limpiar la información de la sesión
    request.session.flush()  # Elimina todos los datos de la sesión

    # Opcional: Agregar un mensaje de confirmación de cierre de sesión
    messages.success(request, "Has cerrado sesión exitosamente.")

    # Redirigir al usuario a la página de inicio de sesión
    return redirect('send_code')  # Cambia 'login' por el nombre de tu URL para la página de inicio de sesión
def chatbot_interface(request):
    return render(request, "chatbot.html")
@csrf_exempt  # Evita problemas de CSRF, útil solo en desarrollo
def chatbot_responder(request):
    if request.method == "GET":
        pregunta = request.GET.get("pregunta", "").lower()
        try:
            # Busca la respuesta en la base de datos
            respuesta = PreguntaRespuesta.objects.get(pregunta__iexact=pregunta).respuesta
            return JsonResponse({"respuesta": respuesta})
        except PreguntaRespuesta.DoesNotExist:
            # Responde con un mensaje predeterminado si no encuentra la pregunta
            return JsonResponse({"respuesta": "Lo siento, no tengo una respuesta para esa pregunta en este momento."})
    # Si no es un método GET, responde con un error
    return JsonResponse({"error": "Método no permitido"}, status=405)

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id_producto=producto_id)
    
    # Obtener el ID del usuario desde la sesión
    user_id = request.session.get('user_id')
    
    if not user_id:
        messages.error(request, 'Debes iniciar sesión para agregar productos al carrito.')
        return redirect('login')

    # Obtener la cuenta asociada al usuario
    cuenta = get_object_or_404(Cuenta, id_usuario=user_id)
    
    # Obtener o crear el carrito para el usuario
    carrito, created = Carrito.objects.get_or_create(id_cuenta=cuenta)
    
    # Crear o actualizar el detalle del carrito
    detalle, created = DetalleCarrito.objects.get_or_create(id_carrito=carrito, id_producto=producto)
    
    # Calcular el total del carrito
    carrito.total = sum(detalle.id_producto.precio for detalle in carrito.detalles.all())
    carrito.save()
    
    messages.success(request, f'{producto.nombre} agregado al carrito.')
    return redirect('productos-compra')  # Redirige a la tienda o donde necesites

def listar_productos(request):
    productos_list = Producto.objects.all()  # Obtener todos los productos
    paginator = Paginator(productos_list, 12)  # Número de productos por página (opcional)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'productos.html', {'page_obj': page_obj})

def mostrar_carrito(request):
    user_id = request.session.get('user_id')  # Obtener el ID del usuario de la sesión
    
    
    # Obtener la cuenta del padre basada en el user_id de la sesión
    cuenta_padre = get_object_or_404(Cuenta, id_usuario=user_id)

    # Lista para guardar los detalles del carrito de cuentas padre e hijos
    detalles_carrito = []
    
    # Buscar cuentas hijas relacionadas al padre en la tabla DetallePadreHijo
    cuentas_ids = DetallePadreHijo.objects.filter(
        id_cuenta_padre=cuenta_padre
    ).values_list('id_cuenta_hijo', flat=True)
    cuentas_ids = list(cuentas_ids) + [cuenta_padre.id_cuenta]

    # Obtener los carritos de las cuentas padre e hijos
    carritos = Carrito.objects.filter(id_cuenta__in=cuentas_ids)

    # Iterar por cada carrito para obtener los detalles con la etiqueta de "Padre" o "Hijo"
    for carrito in carritos:
        detalles = DetalleCarrito.objects.filter(id_carrito=carrito).select_related('id_producto')
        
        for detalle in detalles:
            detalles_carrito.append({
                'id_carrito': carrito.id_carrito,
                'total': carrito.total,
                'nombre_producto': detalle.id_producto.nombre,
                'precio_producto': detalle.id_producto.precio,
                'id_detalle_carrito': detalle.id_detalle_carrito,
                'id_cuenta_propietario': carrito.id_cuenta.id_cuenta,
                'tipo_cuenta': 'Padre' if carrito.id_cuenta == cuenta_padre else 'Hijo',
            })

    # Renderizar el template con los detalles del carrito
    return render(request, 'carrito.html', {
        'detalles_carrito': detalles_carrito,
    })
def eliminar_producto_carrito(request, producto_id):
    detalle = get_object_or_404(DetalleCarrito, id_detalle_carrito=producto_id)
    detalle.delete()
    return redirect('carrito')  # Redirige a la página del carrito


def realizar_venta(request):
    user_id = request.session.get('user_id')
    try:
        # Obtener cuenta del usuario
        cuenta = Cuenta.objects.get(id_usuario=user_id)

        # Verificar si la cuenta tiene el tipo 1 (padre autorizado para realizar compras)
        if cuenta.tipo_cuenta != 1:  # Cambiado a '1' si el tipo_cuenta es un CharField
            return HttpResponse("""
                <script>
                    alert("Lo siento, no tienes autorización para realizar compras.");
                    window.location.href = 'carrito';  // Redirigir al carrito
                </script>
            """)

        # Obtener el carrito del padre
        carrito_padre = Carrito.objects.get(id_cuenta=cuenta)
        detalles_carrito_padre = DetalleCarrito.objects.filter(id_carrito=carrito_padre)

        # Obtener los hijos del padre a través de la tabla DetallePadreHijo
        detalle_padre_hijo = DetallePadreHijo.objects.filter(id_cuenta_padre=cuenta.id_cuenta)
        hijos = [detalle.id_cuenta_hijo for detalle in detalle_padre_hijo]

        # Verificar si el padre o los hijos tienen carritos con productos
        if not detalles_carrito_padre.exists() and not any(Carrito.objects.filter(id_cuenta=hijo).exists() for hijo in hijos):
            return redirect('carrito')  # Aquí puedes agregar un mensaje de "Carrito vacío" en la página

        # Crear una nueva venta para el padre
        venta_padre = Venta.objects.create(id_cuenta=cuenta, fecha=timezone.now())

        # Crear los detalles de la venta del carrito del padre
        for detalle in detalles_carrito_padre:
            DetalleVenta.objects.create(
                id_venta=venta_padre,
                id_producto=detalle.id_producto
            )

        # Calcular el total de la venta del padre
        total_padre = sum(detalle.id_producto.precio for detalle in detalles_carrito_padre)

        # Procesar los carritos de los hijos
        total_hijos = 0
        for hijo in hijos:
            carrito_hijo = Carrito.objects.filter(id_cuenta=hijo).first()
            if carrito_hijo:
                detalles_carrito_hijo = DetalleCarrito.objects.filter(id_carrito=carrito_hijo)

                # Crear una venta para cada hijo
                venta_hijo = Venta.objects.create(id_cuenta=hijo, fecha=timezone.now())

                for detalle in detalles_carrito_hijo:
                    DetalleVenta.objects.create(
                        id_venta=venta_hijo,
                        id_producto=detalle.id_producto
                    )

                # Calcular el total del carrito del hijo
                total_hijos += sum(detalle.id_producto.precio for detalle in detalles_carrito_hijo)

                # Limpiar el carrito del hijo
                detalles_carrito_hijo.delete()
                carrito_hijo.total = 0
                carrito_hijo.save()

        # Limpiar el carrito del padre después de la venta
        detalles_carrito_padre.delete()
        carrito_padre.total = 0
        carrito_padre.save()

        # Calcular el total general (padre + hijos)
        total_general = total_padre + total_hijos

        # Mostrar alerta de éxito con JavaScript
        return HttpResponse(f"""
            <script>
                alert("Venta exitosa, el total de tu compra es: {total_general}. Tu pedido está siendo procesado.");
                window.location.href = 'carrito';  // Redirigir a la página principal o la que prefieras
            </script>
        """)

    except (Cuenta.DoesNotExist, Carrito.DoesNotExist):
        # Redirigir al carrito si no se encuentra una cuenta o carrito
        return redirect('shop')