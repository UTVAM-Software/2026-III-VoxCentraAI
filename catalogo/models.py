from django.core.exceptions import ValidationError
from django.db import models

from comercios.models import Comercio, Sucursal


class Categoria(models.Model):
    id_categoria = models.BigAutoField(primary_key=True)
    comercio = models.ForeignKey(
        Comercio,
        on_delete=models.CASCADE,
        related_name="categorias",
        db_column="comercio_id",
    )
    categoria_padre = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategorias",
        db_column="categoria_padre_id",
    )
    nombre = models.CharField(max_length=120)
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = "CATEGORIA"
        indexes = [models.Index(fields=["comercio", "activa"], name="ix_categoria_com_activa")]
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    id_producto = models.BigAutoField(primary_key=True)
    comercio = models.ForeignKey(
        Comercio,
        on_delete=models.CASCADE,
        related_name="productos",
        db_column="comercio_id",
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="productos",
        db_column="id_categoria",
    )
    sku = models.CharField(max_length=60, null=True, blank=True)
    nombre = models.CharField(max_length=160)
    descripcion = models.TextField(null=True, blank=True)
    precio_base = models.DecimalField(max_digits=12, decimal_places=2)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "PRODUCTO"
        constraints = [
            models.UniqueConstraint(
                fields=["comercio", "sku"],
                condition=models.Q(sku__isnull=False) & ~models.Q(sku=""),
                name="uq_producto_comercio_sku",
            )
        ]
        indexes = [
            models.Index(fields=["comercio", "categoria", "activo"], name="ix_prod_com_cat_act")
        ]
        ordering = ["nombre"]

    def clean(self):
        if self.categoria_id and self.comercio_id and self.categoria.comercio_id != self.comercio_id:
            raise ValidationError({"categoria": "La categoría debe pertenecer al mismo comercio."})

    def __str__(self):
        return self.nombre


class SucursalProducto(models.Model):
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.CASCADE,
        related_name="productos_disponibles",
        db_column="id_sucursal",
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="sucursales_disponibles",
        db_column="id_producto",
    )
    precio_override = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    disponible = models.BooleanField(default=True)
    pk = models.CompositePrimaryKey("sucursal_id", "producto_id")

    class Meta:
        db_table = "SUCURSAL_PRODUCTO"

    def clean(self):
        if (
            self.sucursal_id
            and self.producto_id
            and self.sucursal.comercio_id != self.producto.comercio_id
        ):
            raise ValidationError("La sucursal y el producto deben pertenecer al mismo comercio.")

    def __str__(self):
        return "{} - {}".format(self.sucursal, self.producto)


class GrupoOpcion(models.Model):
    id_grupo = models.BigAutoField(primary_key=True)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name="grupos_opcion",
        db_column="id_producto",
    )
    nombre = models.CharField(max_length=120)
    min_selecciones = models.IntegerField(default=0)
    max_selecciones = models.IntegerField(null=True, blank=True)
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = "GRUPO_OPCION"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return "{}: {}".format(self.producto, self.nombre)


class OpcionProducto(models.Model):
    id_opcion = models.BigAutoField(primary_key=True)
    grupo = models.ForeignKey(
        GrupoOpcion,
        on_delete=models.CASCADE,
        related_name="opciones",
        db_column="id_grupo",
    )
    nombre = models.CharField(max_length=120)
    precio_adicional = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    activa = models.BooleanField(default=True)
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = "OPCION_PRODUCTO"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre
