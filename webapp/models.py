from django.db import models

# Create your models here.

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contraseña = models.CharField(max_length=255)

    class Meta:
        db_table = 'usuario'  # El nombre de la tabla en la base de datos
        managed = False  # Django no gestionará esta tabla

class CodAuth(models.Model):
    id_cod = models.AutoField(primary_key=True)
    cod_auth = models.CharField(max_length=255)

    class Meta:
        db_table = 'cod_auth'
        managed = False

class Cuenta(models.Model):
    id_cuenta = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, db_column='id_usuario', on_delete=models.CASCADE)
    tipo_cuenta = models.CharField(max_length=50)

    class Meta:
        db_table = 'cuenta'  # Nombre de la tabla en la base de datos
        managed = False  # No se gestionarán las migraciones para esta tabla
class DetallePadreHijo(models.Model):
    id_parentezco = models.AutoField(primary_key=True)
    id_cuenta_padre = models.ForeignKey(Cuenta, related_name='padres', db_column='id_cuenta_padre', on_delete=models.CASCADE)
    id_cuenta_hijo = models.ForeignKey(Cuenta, related_name='hijos', db_column='id_cuenta_hijo', on_delete=models.CASCADE)

    class Meta:
        db_table = 'detalle_padre_hijo'
        managed = False  # No se gestionarán las migraciones para esta tabla

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    existencia = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to='images/', blank=True, null=True)

    class Meta:
        db_table = 'producto'
        managed = False

    def __str__(self):
        return self.nombre
    
class PreguntaRespuesta(models.Model):
    pregunta = models.CharField(max_length=255)
    respuesta = models.TextField()

    class Meta:
        db_table = 'preguntarespuesta'  # Nombre de la tabla en la base de datos
        managed = False  # Django no intentará crear ni gestionar esta tabla

    def __str__(self):
        return self.pregunta

class Carrito(models.Model):
    id_carrito = models.AutoField(primary_key=True)
    id_cuenta = models.ForeignKey('Cuenta', null=True, blank=True, on_delete=models.SET_NULL, db_column='id_cuenta')
    total = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'carrito'
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

class DetalleCarrito(models.Model):
    id_detalle_carrito = models.AutoField(primary_key=True)
    id_carrito = models.ForeignKey(Carrito, null=True, blank=True, on_delete=models.SET_NULL, db_column='id_carrito', related_name='detalles')
    id_producto = models.ForeignKey('Producto', null=True, blank=True, on_delete=models.SET_NULL, db_column='id_producto')

    class Meta:
        db_table = 'detalle_carrito'
        verbose_name = 'Detalle Carrito'
        verbose_name_plural = 'Detalles Carrito'
class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, db_column='id_cuenta')  # Especificamos db_column
    fecha = models.DateField(auto_now_add=True)

    class Meta:
        managed = False  # No se manejará la migración de esta tabla
        db_table = 'venta'  # Nombre de la tabla en la base de datos
        verbose_name = 'Venta'  # Nombre singular
        verbose_name_plural = 'Ventas'  # Nombre plural


class DetalleVenta(models.Model):
    id_venta_detalle = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE, db_column='id_venta')  # Especificamos db_column
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE, db_column='id_producto')  # Especificamos db_column

    class Meta:
        managed = False  # No se manejará la migración de esta tabla
        db_table = 'detalle_venta'  # Nombre de la tabla en la base de datos
        verbose_name = 'Detalle de Venta'  # Nombre singular
        verbose_name_plural = 'Detalles de Venta'  # Nombre plural