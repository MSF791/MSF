from django.db import models
from django.contrib.auth.models import User


class Stock(models.TextChoices):
    si = 'si'
    no = 'no'

#agregar colores en opciones
class Colors(models.TextChoices):
    blanco = 'Blanco'
    negro = 'Negro'
    naranja = 'Naranja'
    azul = 'Azul'
    amarillo = 'Amarillo'
    cafe = 'Cafe'
    rojo = 'Rojo'

#agregar tallas en opciones
class Tallas(models.TextChoices):
    extra_pequeña = 'XS'
    pequeña = 'S'
    mediana = 'M'
    grande = 'L'
    extra_grande = 'XL'

#categorias
class Categorias(models.Model):
    nombre = models.CharField(max_length=100, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre=models.CharField(max_length=30)
    descripcion=models.CharField(max_length=500)
    precio=models.IntegerField(default='0')
    stock=models.CharField(max_length=3, choices=Stock)
    imagen = models.ImageField(upload_to='imagenes', null=True)
    en_lista_deseos = models.BooleanField(default=False)
    #actualizacion para detalles del producto
    color = models.CharField(max_length=50, choices=Colors, default='Blanco')
    talla = models.CharField(max_length=50, choices=Tallas, default='S')
    categoria = models.ManyToManyField(Categorias)

class ItemCarrito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)  # Establecer un valor predeterminado

    def subtotal(self):
        return self.producto.precio * self.cantidad

class Carrito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    items = models.ManyToManyField(ItemCarrito)

#chat
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    message = models.CharField(max_length=1200)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message

    class Meta:
        ordering = ('timestamp',)