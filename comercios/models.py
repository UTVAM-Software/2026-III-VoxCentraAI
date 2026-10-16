from django.db import models


class Comercio(models.Model):
    id_comercio = models.BigAutoField(primary_key=True)
    nombre_comercial = models.CharField(max_length=160)
    slug = models.SlugField(max_length=100, unique=True)
    giro = models.CharField(max_length=80)
    moneda = models.CharField(max_length=3, default="MXN")
    zona_horaria = models.CharField(max_length=60, default="America/Mexico_City")
    estado = models.CharField(max_length=20, default="activo")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "COMERCIO"
        ordering = ["nombre_comercial"]

    def __str__(self):
        return self.nombre_comercial


class Sucursal(models.Model):
    id_sucursal = models.BigAutoField(primary_key=True)
    comercio = models.ForeignKey(
        Comercio,
        on_delete=models.PROTECT,
        related_name="sucursales",
        db_column="comercio_id",
    )
    nombre = models.CharField(max_length=120)
    direccion = models.TextField()
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = "SUCURSAL"
        indexes = [models.Index(fields=["comercio", "activa"], name="ix_sucursal_com_activa")]
        ordering = ["comercio", "nombre"]

    def __str__(self):
        return f"{self.comercio}: {self.nombre}"


class ConfiguracionComercio(models.Model):
    comercio = models.OneToOneField(
        Comercio,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="configuracion",
        db_column="comercio_id",
    )
    saludo = models.TextField(blank=True)
    instrucciones_atencion = models.TextField(blank=True)
    canal_voz_activo = models.BooleanField(default=False)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "CONFIGURACION_COMERCIO"

    def __str__(self):
        return f"Configuración de {self.comercio}"
