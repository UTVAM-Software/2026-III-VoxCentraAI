from django.contrib import admin

from .models import Categoria, GrupoOpcion, OpcionProducto, Producto


admin.site.register(Categoria)
admin.site.register(Producto)
admin.site.register(GrupoOpcion)
admin.site.register(OpcionProducto)
