# VoxCentraAI

¿Tu negocio recibe pedidos por teléfono mientras estás ocupado? Con VoxCentraAI, una asistente virtual contesta, conversa con el cliente y toma su pedido usando el menú que registraste. Cuando repasa los datos y el cliente los confirma, el pedido queda en tu panel para que puedas revisarlo y prepararlo.

## ¿Qué puedes hacer?

- Registrar comercios, sucursales, productos, precios y disponibilidad.
- Consultar clientes y sus direcciones.
- Probar una conversación por voz y pedirle a la asistente que tome un pedido.
- Ver el pedido con sus productos, cantidades, entrega, dirección, forma de pago y total.
- Consultar llamadas anteriores y el estado de cada pedido.
- Dar acceso a otras personas como administradores, operadores o usuarios de solo lectura.
- Ver los pedidos nuevos en el panel sin recargar la página.

La asistente usa la información del comercio seleccionado. Así puede consultar su menú y precios al atender.

### Sobre las llamadas

En esta versión puedes probar la conversación desde la página web usando el micrófono de tu computadora. La conexión a un número telefónico real todavía está pendiente; por ahora, la prueba se hace desde el navegador.

Para usar la voz necesitas configurar tus propias claves de Groq y Deepgram en un archivo `.env`.

## Cuentas para revisar la entrega

Estas cuentas están incluidas en los datos de demostración. Las contraseñas distinguen mayúsculas y minúsculas.

| Usuario | Acceso | Contraseña |
| --- | --- | --- |
| `demo_admin` | Administrador de demostración | `iEFLK_5Rzw1whEGOmYEh1Rwb` |
| `demo_operador` | Operación del comercio | `ID4Oq4dm8E9cKvfE2QU59XGk` |
| `demo_lector` | Solo lectura | `JNilqrEzwJmTHt61iVc2NxP2` |

Para que estas contraseñas funcionen igual al instalar el proyecto en otra computadora, carga los datos de demostración con `loaddata`, como se muestra abajo. Si usas `seed_voxcentra`, se generan claves nuevas y el comando las muestra en la terminal.

Estas son cuentas de prueba para la entrega escolar. Comparte este README de forma privada y cambia las claves antes de publicar el proyecto en un repositorio público.

Los datos que agrega la demostración, incluido un pedido de ejemplo, son ficticios. No prepares ni entregues ese pedido.

## Instalación local tipo preproducción

El instalador prepara el entorno virtual, descarga o copia el proyecto, configura la base local, instala las dependencias de Django, aplica las migraciones, carga las cuentas de demostración en una base nueva y activa el servicio web.

Abre PowerShell en la carpeta donde guardaste instalar.ps1:

~~~powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\instalar.ps1 -InstallPath "$env:LOCALAPPDATA\VoxCentraAI-preproduccion"
~~~

Ese comando descarga la rama main desde GitHub. Si quieres instalar una copia local que ya tienes en tu computadora, indica su carpeta:

~~~powershell
.\instalar.ps1 -SourcePath "C:\ruta\al\proyecto" -InstallPath "$env:LOCALAPPDATA\VoxCentraAI-preproduccion"
~~~

El servicio queda disponible solo en esta computadora, en http://127.0.0.1:8000/. Para detenerlo, ejecuta .\detener-local.ps1 dentro de la carpeta de instalación. Si instalas desde GitHub, agrega tus claves de Groq y Deepgram al archivo .env para probar las llamadas.
## Cuida tus claves

- Las claves de la tabla son solo para la demostración escolar; no las uses en un sistema público.
- No compartas ni subas `.env` ni la base de datos `db.sqlite3`.
- Si publicas una instalación para que otras personas la usen, cambia las claves de demostración y crea sus cuentas desde el panel.
