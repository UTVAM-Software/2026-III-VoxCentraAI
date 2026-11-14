# Datos de demostración

El proyecto incluye `documentacion/voxcentra_seed.json`, una copia preparada desde una base limpia. Contiene datos ficticios del comercio, sucursal, catálogo, clientes, pedidos y las tres cuentas demo documentadas en el README.

## Cargar los datos

Desde la carpeta que contiene `manage.py`, después de instalar los requisitos y crear la base local:

```powershell
python manage.py migrate
python manage.py loaddata documentacion/voxcentra_seed.json
```

El instalador también prepara el entorno y ejecuta las migraciones. En ese caso, carga el fixture con el segundo comando. No ejecutes `seed_voxcentra` después de importar el fixture.

## Crear datos nuevos

Si prefieres generar otra base de demostración desde cero, puedes ejecutar:

```powershell
python manage.py migrate
python manage.py seed_voxcentra
```

Ese comando crea las cuentas demo y muestra sus contraseñas temporales al crearlas. Las contraseñas de una base creada así serán distintas a las de la tabla del README.

El fixture público solo debe usarse en instalaciones locales de práctica. Sus cuentas son de demostración y no deben reutilizarse en otros sistemas ni exponerse en un servidor público. Las claves de Groq y Deepgram van en `.env` y no se incluyen en el repositorio.
