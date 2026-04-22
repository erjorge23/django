from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    tienda = models.CharField(max_length=100)
    precio = models.CharField(max_length=50) 
    link = models.URLField(max_length=500)
    imagen = models.URLField(max_length=500, null=True, blank=True)
    tiene_stock = models.BooleanField(default=True)
    valoracion = models.CharField(max_length=50, null=True, blank=True)
    fecha_busqueda = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.tienda}"

class Favorito(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'producto')

    def __str__(self):
        return f"{self.user.username} -> {self.producto.nombre}"