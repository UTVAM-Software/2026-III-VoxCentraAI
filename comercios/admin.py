from django.contrib import admin

from .models import Comercio, ConfiguracionComercio, Sucursal


admin.site.register(Comercio)
admin.site.register(Sucursal)
admin.site.register(ConfiguracionComercio)
