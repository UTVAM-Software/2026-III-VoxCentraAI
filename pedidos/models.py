from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from catalogo.models import OpcionProducto, Producto
from clientes.models import Cliente
from comercios.models import Comercio, Sucursal
from interacciones.models import Interaccion


class Pedido(models.Model):
    id_pedido = models.BigAutoField(primary_key=True)
    comercio = models.ForeignKey(
        Comercio,
        on_delete=models.PROTECT,
        related_name="pedidos",
        db_column="comercio_id",
    )
    sucursal = models.ForeignKey(
        Sucursal,
        on_delete=models.PROTECT,
        related_name="pedidos",
        db_column="id_sucursal",
    )
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos",
        db_column="id_cliente",
    )
    interaccion = models.ForeignKey(
        Interaccion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos",
        db_column="id_interaccion",
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos_creados",
        db_column="creado_por",
    )
    origen = models.CharField(max_length=24)
    estado = models.CharField(max_length=24)
    tipo_entrega = models.CharField(max_length=20)
    moneda = models.CharField(max_length=3, default="MXN")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notas = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "PEDIDO"
        indexes = [
            models.Index(
                fields=["comercio", "estado", "creado_en"],
                name="ix_pedido_com_est_fecha",
            )
        ]
        ordering = ["-creado_en"]

    def clean(self):
        if self.sucursal_id and self.sucursal.comercio_id != self.comercio_id:
            raise ValidationError({"sucursal": "La sucursal debe pertenecer al mismo comercio."})
        if self.cliente_id and self.cliente.comercio_id != self.comercio_id:
            raise ValidationError({"cliente": "El cliente debe pertenecer al mismo comercio."})
        if self.interaccion_id and self.interaccion.comercio_id != self.comercio_id:
            raise ValidationError({"interaccion": "La interacción debe pertenecer al mismo comercio."})

    def __str__(self):
        return f"Pedido {self.id_pedido}"


class DireccionPedido(models.Model):
    pedido = models.OneToOneField(
        Pedido,
        on_delete=models.PROTECT,
        primary_key=True,
        related_name="direccion_entrega",
        db_column="id_pedido",
    )
    calle = models.CharField(max_length=160)
    numero_exterior = models.CharField(max_length=20)
    numero_interior = models.CharField(max_length=20, null=True, blank=True)
    colonia = models.CharField(max_length=120)
    ciudad = models.CharField(max_length=120)
    codigo_postal = models.CharField(max_length=12, null=True, blank=True)
    referencias = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "DIRECCION_PEDIDO"

    def __str__(self):
        return f"Dirección del pedido {self.pedido_id}"


class DetallePedido(models.Model):
    id_detalle = models.BigAutoField(primary_key=True)
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.PROTECT,
        related_name="detalles",
        db_column="id_pedido",
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detalles_pedido",
        db_column="id_producto",
    )
    sku_snapshot = models.CharField(max_length=60, null=True, blank=True)
    nombre_snapshot = models.CharField(max_length=160)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    notas = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "DETALLE_PEDIDO"

    def clean(self):
        if (
            self.producto_id
            and self.pedido_id
            and self.producto.comercio_id != self.pedido.comercio_id
        ):
            raise ValidationError({"producto": "El producto debe pertenecer al comercio del pedido."})

    def __str__(self):
        return self.nombre_snapshot


class OpcionDetalle(models.Model):
    id_opcion_detalle = models.BigAutoField(primary_key=True)
    detalle = models.ForeignKey(
        DetallePedido,
        on_delete=models.PROTECT,
        related_name="opciones",
        db_column="id_detalle",
    )
    opcion_producto = models.ForeignKey(
        OpcionProducto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="detalles_pedido",
        db_column="id_opcion_producto",
    )
    grupo_snapshot = models.CharField(max_length=120)
    opcion_snapshot = models.CharField(max_length=120)
    precio_adicional_snapshot = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        db_table = "OPCION_DETALLE"

    def clean(self):
        if (
            self.opcion_producto_id
            and self.detalle_id
            and self.detalle.producto_id
            and self.opcion_producto.grupo.producto_id != self.detalle.producto_id
        ):
            raise ValidationError({"opcion_producto": "La opción debe pertenecer al producto del detalle."})

    def __str__(self):
        return self.opcion_snapshot


class Pago(models.Model):
    id_pago = models.BigAutoField(primary_key=True)
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.PROTECT,
        related_name="pagos",
        db_column="id_pedido",
    )
    metodo = models.CharField(max_length=24)
    estado = models.CharField(max_length=24)
    importe = models.DecimalField(max_digits=12, decimal_places=2)
    referencia_externa = models.CharField(max_length=140, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    pagado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "PAGO"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Pago {self.id_pago} - pedido {self.pedido_id}"


class HistorialPedido(models.Model):
    id_evento = models.BigAutoField(primary_key=True)
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.PROTECT,
        related_name="historial",
        db_column="id_pedido",
    )
    estado_anterior = models.CharField(max_length=24, null=True, blank=True)
    estado_nuevo = models.CharField(max_length=24)
    cambiado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cambios_pedido",
        db_column="cambiado_por",
    )
    nota = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "HISTORIAL_PEDIDO"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Pedido {self.pedido_id}: {self.estado_nuevo}"
