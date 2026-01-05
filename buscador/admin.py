from django.contrib import admin
from .models import Producto

class ProductoAdmin(admin.ModelAdmin):
    # Qué columnas verás en la lista
    list_display = ('nombre', 'precio', 'tienda', 'valoracion', 'tiene_stock', 'fecha_busqueda')
    
    # Barra lateral de filtros (muy útil)
    list_filter = ('tienda', 'tiene_stock', 'fecha_busqueda')
    
    # Barra de búsqueda (busca por nombre del producto)
    search_fields = ('nombre',)
    
    # Para que no se pueda editar la fecha de búsqueda manualmente (es automática)
    readonly_fields = ('fecha_busqueda',)

# Registramos el modelo con esta configuración
admin.site.register(Producto, ProductoAdmin)