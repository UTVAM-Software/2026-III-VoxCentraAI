import secrets
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction

from accesos.models import MembresiaComercio
from catalogo.models import Categoria, Producto, SucursalProducto
from clientes.models import Cliente, DireccionCliente
from comercios.models import Comercio, ConfiguracionComercio, Sucursal
from interacciones.models import Interaccion
from pedidos.models import (
    DetallePedido,
    DireccionPedido,
    HistorialPedido,
    Pago,
    Pedido,
)


class Command(BaseCommand):
    help = "Crea o completa datos ficticios idempotentes para probar VoxCentraAI."

    def _create_demo_user(self, username, email, *, superuser=False):
        User = get_user_model()
        user = User.objects.filter(username=username).first()
        if user:
            return user, None
        password = secrets.token_urlsafe(18)
        if superuser:
            user = User.objects.create_superuser(username=username, email=email, password=password)
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
        return user, password

    @transaction.atomic
    def handle(self, *args, **options):
        commerce, _ = Comercio.objects.get_or_create(
            slug="voxcentra-demo",
            defaults={
                "nombre_comercial": "VoxCentraAI · Restaurante de demostración",
                "giro": "Restaurante de comida rápida",
                "moneda": "MXN",
                "estado": "activo",
            },
        )
        branch, _ = Sucursal.objects.get_or_create(
            comercio=commerce,
            nombre="Sucursal de prueba",
            defaults={"direccion": "Av. Ficticia 100, Colonia Centro, Ciudad de México"},
        )
        ConfiguracionComercio.objects.get_or_create(
            comercio=commerce,
            defaults={
                "saludo": f"Buenas tardes, le atiende Lucía, asistente virtual de {commerce.nombre_comercial}. ¿Qué le gustaría ordenar?",
                "instrucciones_atencion": "Atiende con amabilidad. Confirma productos, cantidades, entrega y total antes de registrar el pedido.",
                "canal_voz_activo": True,
            },
        )

        product_rows = [
            ("Pizzas", "PIZ-PEP", "Pizza de Pepperoni", "Pizza tradicional con pepperoni.", "150.00"),
            ("Pizzas", "PIZ-HAW", "Pizza Hawaiana", "Pizza con jamón y piña.", "160.00"),
            ("Hamburguesas", "HAM-CLA", "Hamburguesa Clásica", "Carne, queso, lechuga y tomate.", "90.00"),
            ("Bebidas", "BEB-COL-600", "Refresco de Cola 600 ml", "Refresco embotellado de 600 ml.", "30.00"),
            ("Bebidas", "BEB-AGU-500", "Agua natural 500 ml", "Botella de agua natural.", "20.00"),
            ("Combos", "COM-PIZ-COL", "Combo Pizza Pepperoni", "Pizza de pepperoni y refresco de cola de 600 ml.", "170.00"),
            ("Combos", "COM-HAM-COL", "Combo Hamburguesa", "Hamburguesa clásica y refresco de cola de 600 ml.", "110.00"),
            ("Complementos", "COM-PAP-CLA", "Papas clásicas", "Porción individual de papas.", "45.00"),
            ("Complementos", "COM-EXT-QUE", "Extra queso", "Porción de queso adicional.", "25.00"),
        ]
        products = {}
        for category_name, sku, name, description, price in product_rows:
            category, _ = Categoria.objects.get_or_create(
                comercio=commerce,
                nombre=category_name,
                defaults={"activa": True},
            )
            product, _ = Producto.objects.update_or_create(
                comercio=commerce,
                sku=sku,
                defaults={
                    "categoria": category,
                    "nombre": name,
                    "descripcion": description,
                    "precio_base": Decimal(price),
                    "activo": True,
                },
            )
            SucursalProducto.objects.update_or_create(
                sucursal=branch,
                producto=product,
                defaults={"precio_override": None, "disponible": True},
            )
            products[sku] = product

        User = get_user_model()
        demo_admin, admin_password = self._create_demo_user(
            "demo_admin", "demo_admin@example.test", superuser=True
        )
        demo_operator, operator_password = self._create_demo_user(
            "demo_operador", "demo_operador@example.test"
        )
        demo_reader, reader_password = self._create_demo_user(
            "demo_lector", "demo_lector@example.test"
        )

        app_labels = ("comercios", "catalogo", "clientes", "interacciones", "pedidos")
        permissions = Permission.objects.filter(content_type__app_label__in=app_labels)
        reader_group, _ = Group.objects.get_or_create(name="VoxCentra Demo · Solo lectura")
        reader_group.permissions.set(permissions.filter(codename__startswith="view_"))
        operator_group, _ = Group.objects.get_or_create(name="VoxCentra Demo · Operación")
        operator_group.permissions.set(
            permission
            for permission in permissions
            if permission.codename.startswith(("view_", "add_", "change_"))
            and not permission.codename.startswith("delete_")
        )
        demo_operator.groups.add(operator_group)
        demo_reader.groups.add(reader_group)

        for username, role in (
            (demo_admin, "Administrador"),
            (demo_operator, "Operación"),
            (demo_reader, "Solo lectura"),
        ):
            MembresiaComercio.objects.get_or_create(
                usuario=username,
                comercio=commerce,
                defaults={"rol": role, "activo": True},
            )

        sample_client, _ = Cliente.objects.get_or_create(
            comercio=commerce,
            nombre="Cliente ficticio de prueba",
            defaults={"telefono": "+52 55 0000 0001", "correo": "cliente@example.test"},
        )
        DireccionCliente.objects.get_or_create(
            cliente=sample_client,
            alias="Domicilio de prueba",
            defaults={
                "calle": "Calle Ficticia",
                "numero_exterior": "100",
                "colonia": "Centro",
                "ciudad": "Ciudad de México",
                "codigo_postal": "06000",
                "referencias": "Dirección de demostración; no corresponde a un domicilio real.",
                "predeterminada": True,
            },
        )

        interaction = Interaccion.objects.filter(
            comercio=commerce, referencia_externa="SEED-VOZ-001"
        ).first()
        if interaction is None:
            interaction = Interaccion.objects.create(
                comercio=commerce,
                sucursal=branch,
                cliente=sample_client,
                canal="voz_prueba",
                estado="pedido registrado",
                referencia_externa="SEED-VOZ-001",
            )

        order = Pedido.objects.filter(interaccion=interaction).first()
        if order is None:
            pizza = products["PIZ-PEP"]
            drink = products["BEB-COL-600"]
            order = Pedido.objects.create(
                comercio=commerce,
                sucursal=branch,
                cliente=sample_client,
                interaccion=interaction,
                creado_por=demo_operator,
                origen="seed_demo",
                estado="recibido",
                tipo_entrega="domicilio",
                moneda=commerce.moneda,
                subtotal=Decimal("180.00"),
                descuento=Decimal("0.00"),
                impuestos=Decimal("0.00"),
                total=Decimal("180.00"),
                notas="PEDIDO FICTICIO DE SEED PARA PRUEBAS. No preparar ni entregar.",
            )
            DetallePedido.objects.create(
                pedido=order, producto=pizza, sku_snapshot=pizza.sku,
                nombre_snapshot=pizza.nombre, cantidad=1,
                precio_unitario=Decimal("150.00"), notas="Sin cambios; dato ficticio.",
            )
            DetallePedido.objects.create(
                pedido=order, producto=drink, sku_snapshot=drink.sku,
                nombre_snapshot=drink.nombre, cantidad=1,
                precio_unitario=Decimal("30.00"), notas="",
            )
            DireccionPedido.objects.create(
                pedido=order,
                calle="Calle Ficticia",
                numero_exterior="100",
                colonia="Centro",
                ciudad="Ciudad de México",
                codigo_postal="06000",
                referencias="Domicilio ficticio de demostración. No corresponde a un domicilio real.",
            )
            Pago.objects.create(
                pedido=order, metodo="efectivo", estado="pendiente",
                importe=order.total,
            )
            HistorialPedido.objects.create(
                pedido=order, estado_nuevo=order.estado, cambiado_por=demo_operator,
                nota="Registro ficticio creado por seed_voxcentra.",
            )

        self.stdout.write(self.style.SUCCESS(
            f"Semilla lista: comercio {commerce.slug}, 1 sucursal, {len(product_rows)} productos, "
            "3 cuentas demo, 1 cliente ficticio y 1 pedido de ejemplo."
        ))
        for username, password in (
            ("demo_admin", admin_password),
            ("demo_operador", operator_password),
            ("demo_lector", reader_password),
        ):
            if password:
                self.stdout.write(self.style.WARNING(f"Cuenta nueva: {username} | contraseña temporal: {password}"))
            else:
                self.stdout.write(f"Cuenta existente sin cambios: {username}")
