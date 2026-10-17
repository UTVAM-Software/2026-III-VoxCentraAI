from django.core.exceptions import ValidationError
from django.db import models

from clientes.models import Cliente
from comercios.models import Comercio, Sucursal


class Interaccion(models.Model):
    id_interaccion = models.BigAutoField(primary_key=True)
    comercio = models.ForeignKey(
        Comercio,
        on_delete=models.PROTECT,
        related_name="interacciones",
        db_column="comercio_id",
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interacciones",
        db_column="id_sucursal",
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interacciones",
        db_column="id_cliente",
    )
    canal = models.CharField(max_length=24)
    estado = models.CharField(max_length=24)
    iniciada_en = models.DateTimeField(auto_now_add=True)
    terminada_en = models.DateTimeField(null=True, blank=True)
    referencia_externa = models.CharField(max_length=120, null=True, blank=True)

    class Meta:
        db_table = "INTERACCION"
        ordering = ["-iniciada_en"]

    def clean(self):
        if self.sucursal_id and self.sucursal.comercio_id != self.comercio_id:
            raise ValidationError({"sucursal": "La sucursal debe pertenecer al mismo comercio."})
        if self.cliente_id and self.cliente.comercio_id != self.comercio_id:
            raise ValidationError({"cliente": "El cliente debe pertenecer al mismo comercio."})

    def __str__(self):
        return "Interacción {} ({})".format(self.id_interaccion, self.canal)
