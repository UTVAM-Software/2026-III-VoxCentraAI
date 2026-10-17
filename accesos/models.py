from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from comercios.models import Comercio, Sucursal


class RolPlataforma(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="rol_plataforma",
        db_column="usuario_id",
    )
    rol = models.CharField(max_length=30)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ROL_PLATAFORMA"

    def __str__(self):
        return f"{self.usuario}: {self.rol}"


class MembresiaComercio(models.Model):
    id_membresia = models.BigAutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="membresias_comercio",
        db_column="usuario_id",
    )
    comercio = models.ForeignKey(
        Comercio,
        on_delete=models.PROTECT,
        related_name="membresias",
        db_column="comercio_id",
    )
    rol = models.CharField(max_length=30)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "MEMBRESIA_COMERCIO"
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "comercio"],
                name="uq_mem_usuario_comercio",
            )
        ]

    def __str__(self):
        return f"{self.usuario} - {self.comercio} ({self.rol})"


class AlcanceSucursal(models.Model):
    membresia = models.ForeignKey(
        MembresiaComercio,
        on_delete=models.CASCADE,
        related_name="alcances_sucursal",
        db_column="id_membresia",
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name="alcances_membresia",
        db_column="id_sucursal",
    )
    pk = models.CompositePrimaryKey("membresia_id", "sucursal_id")

    class Meta:
        db_table = "ALCANCE_SUCURSAL"

    def clean(self):
        if (
            self.membresia_id
            and self.sucursal_id
            and self.membresia.comercio_id != self.sucursal.comercio_id
        ):
            raise ValidationError("La sucursal debe pertenecer al comercio de la membresía.")

    def __str__(self):
        return f"{self.membresia} - {self.sucursal}"
