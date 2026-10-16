from django.db import models

from comercios.models import Comercio


class Cliente(models.Model):
    id_cliente = models.BigAutoField(primary_key=True)
    comercio = models.ForeignKey(
        Comercio,
        on_delete=models.CASCADE,
        related_name="clientes",
        db_column="comercio_id",
    )
    nombre = models.CharField(max_length=160)
    telefono = models.CharField(max_length=25, null=True, blank=True)
    correo = models.EmailField(max_length=254, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "CLIENTE"
        indexes = [models.Index(fields=["comercio", "telefono"], name="ix_cliente_com_tel")]
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class DireccionCliente(models.Model):
    id_direccion = models.BigAutoField(primary_key=True)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="direcciones",
        db_column="id_cliente",
    )
    alias = models.CharField(max_length=60)
    calle = models.CharField(max_length=160)
    numero_exterior = models.CharField(max_length=20)
    numero_interior = models.CharField(max_length=20, null=True, blank=True)
    colonia = models.CharField(max_length=120)
    ciudad = models.CharField(max_length=120)
    codigo_postal = models.CharField(max_length=12, null=True, blank=True)
    referencias = models.TextField(null=True, blank=True)
    predeterminada = models.BooleanField(default=False)

    class Meta:
        db_table = "DIRECCION_CLIENTE"

    def __str__(self):
        return f"{self.alias} - {self.cliente}"
