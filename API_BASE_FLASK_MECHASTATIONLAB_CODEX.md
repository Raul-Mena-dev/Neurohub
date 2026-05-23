# Instrucciones para Codex: API base Flask para Mecha Station Lab

## 1. Contexto del proyecto

Este proyecto será una **API central en Flask** para Mecha Station Lab. La API vivirá en un VPS bajo un subdominio como:

```txt
https://api.mechastationlab.com
```

La API será consumida por diferentes proyectos/subdominios, por ejemplo:

```txt
https://mechastationlab.com              -> landing principal en React estático
https://caramelo.mechastationlab.com     -> catálogo/pedidos web en React estático
https://api.mechastationlab.com          -> API Flask en VPS
```

El POS de Caramelo **no vivirá en el servidor**. El POS funciona localmente/offline con su propia base de datos local. La API servirá para:

- recibir sincronizaciones periódicas desde el POS local;
- guardar catálogo, precios, existencias e imágenes;
- exponer catálogo público a la página web de Caramelo;
- recibir pedidos desde la página web;
- permitir que el POS descargue pedidos pendientes;
- mantener cada proyecto separado por módulos/rutas para facilitar mantenimiento.

Cada proyecto podrá tener su propia base de datos o su propio esquema lógico. La primera implementación debe dejar preparada la estructura para crecer con más proyectos.

---

## 2. Objetivo técnico

Construir una API base con Flask que tenga:

- arquitectura modular;
- enrutamiento separado por proyecto;
- configuración por variables de entorno;
- conexión a base de datos con SQLAlchemy;
- migraciones con Flask-Migrate/Alembic;
- autenticación básica por API Key para sincronización del POS;
- CORS configurado para frontends permitidos;
- endpoints iniciales para health check;
- endpoints base para Caramelo;
- estructura lista para Docker;
- separación clara entre rutas, modelos, servicios y utilidades.

---

## 3. Stack recomendado

Usar:

```txt
Python 3.11+
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-CORS
python-dotenv
Gunicorn
psycopg2-binary o psycopg[binary]
Marshmallow o Pydantic opcional
```

Base de datos recomendada:

```txt
PostgreSQL
```

Para desarrollo local puede usarse SQLite solo si facilita pruebas, pero la configuración principal debe apuntar a PostgreSQL.

---

## 4. Estructura esperada del proyecto

Crear una estructura similar a esta:

```txt
mechastationlab-api/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   │
│   ├── common/
│   │   ├── __init__.py
│   │   ├── responses.py
│   │   ├── decorators.py
│   │   └── errors.py
│   │
│   ├── modules/
│   │   ├── __init__.py
│   │   │
│   │   ├── health/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   │
│   │   ├── caramelo/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   └── services.py
│   │   │
│   │   └── granos/
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       ├── models.py
│   │       ├── schemas.py
│   │       └── services.py
│   │
│   └── wsgi.py
│
├── migrations/
├── tests/
│   ├── __init__.py
│   └── test_health.py
│
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── README.md
└── run.py
```

La idea principal es que cada proyecto tenga su propio módulo dentro de:

```txt
app/modules/<nombre_proyecto>/
```

Por ejemplo:

```txt
app/modules/caramelo/
app/modules/granos/
```

Cada módulo debe poder tener sus propias rutas, modelos, esquemas y servicios.

---

## 5. Patrón de creación de la app

Usar el patrón **Application Factory** de Flask.

Archivo esperado:

```txt
app/__init__.py
```

Debe contener una función:

```python
create_app(config_name=None)
```

Esta función debe:

1. crear la instancia de Flask;
2. cargar configuración;
3. inicializar extensiones;
4. registrar blueprints;
5. registrar manejadores de errores;
6. devolver la app.

Ejemplo conceptual:

```python
from flask import Flask
from app.config import get_config
from app.extensions import db, migrate, cors
from app.modules.health.routes import health_bp
from app.modules.caramelo.routes import caramelo_bp
from app.modules.granos.routes import granos_bp


def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    app.register_blueprint(health_bp, url_prefix="/api/health")
    app.register_blueprint(caramelo_bp, url_prefix="/api/caramelo")
    app.register_blueprint(granos_bp, url_prefix="/api/granos")

    return app
```

---

## 6. Configuración

Crear:

```txt
app/config.py
```

Debe permitir configuración por entorno:

- development;
- testing;
- production.

Variables esperadas:

```env
FLASK_ENV=development
SECRET_KEY=change_me
DATABASE_URL=postgresql://user:password@localhost:5432/mechastationlab_api
CORS_ORIGINS=http://localhost:5173,https://mechastationlab.com,https://caramelo.mechastationlab.com
API_KEY_HEADER=X-API-Key
```

Archivo `.env.example`:

```env
FLASK_ENV=development
SECRET_KEY=change_me
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mechastationlab_api
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://mechastationlab.com,https://caramelo.mechastationlab.com
API_KEY_HEADER=X-API-Key
```

---

## 7. Extensiones

Crear:

```txt
app/extensions.py
```

Debe declarar las extensiones sin inicializarlas directamente con app:

```python
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS


db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
```

---

## 8. Respuestas estándar

Crear:

```txt
app/common/responses.py
```

Debe tener helpers para respuestas JSON consistentes.

Formato recomendado:

```json
{
  "ok": true,
  "message": "Operación exitosa",
  "data": {}
}
```

Para errores:

```json
{
  "ok": false,
  "message": "Descripción del error",
  "errors": {}
}
```

Funciones sugeridas:

```python
def success_response(data=None, message="OK", status_code=200):
    ...


def error_response(message="Error", errors=None, status_code=400):
    ...
```

---

## 9. Decorador de API Key

Crear:

```txt
app/common/decorators.py
```

Debe incluir un decorador para validar API Key en endpoints de sincronización.

La API Key puede validarse inicialmente contra una tabla `caramelo_sucursales` o contra una variable de entorno. Dejarlo preparado para validar contra BD.

Ejemplo de uso:

```python
@caramelo_bp.route("/sync/productos", methods=["POST"])
@require_api_key

def sync_productos():
    ...
```

Encabezado esperado:

```txt
X-API-Key: <api_key>
```

---

## 10. Módulo Health

Crear:

```txt
app/modules/health/routes.py
```

Blueprint:

```python
health_bp = Blueprint("health", __name__)
```

Endpoint:

```txt
GET /api/health
```

Respuesta esperada:

```json
{
  "ok": true,
  "message": "API running",
  "data": {
    "service": "mechastationlab-api"
  }
}
```

---

## 11. Módulo Caramelo

Crear módulo:

```txt
app/modules/caramelo/
```

### 11.1 Blueprint

Archivo:

```txt
app/modules/caramelo/routes.py
```

Blueprint:

```python
caramelo_bp = Blueprint("caramelo", __name__)
```

Prefijo al registrar:

```txt
/api/caramelo
```

---

## 12. Modelos iniciales de Caramelo

Archivo:

```txt
app/modules/caramelo/models.py
```

Crear modelos iniciales con SQLAlchemy.

### 12.1 Sucursal

Tabla sugerida:

```txt
caramelo_sucursales
```

Campos:

```txt
id                    UUID/string primary key o integer
nombre                string
api_key_hash           string nullable inicialmente o api_key simple para MVP
activa                boolean default true
fecha_registro         datetime
fecha_modificacion     datetime
```

### 12.2 Categoría

Tabla:

```txt
caramelo_categorias
```

Campos:

```txt
id                    integer primary key
sucursal_id            FK a caramelo_sucursales
id_local_pos           string
nombre                string
activo                boolean default true
fecha_modificacion_pos datetime nullable
fecha_sincronizacion   datetime
```

### 12.3 Producto

Tabla:

```txt
caramelo_productos
```

Campos:

```txt
id                    integer primary key
sucursal_id            FK a caramelo_sucursales
categoria_id           FK a caramelo_categorias nullable
id_local_pos           string
sku                   string nullable
nombre                string
slug                  string nullable
Descripcion            text nullable
precio                numeric(12, 2)
existencia             numeric(12, 3) default 0
imagen_url             string nullable
activo                boolean default true
visible_web            boolean default true
fecha_modificacion_pos datetime nullable
fecha_sincronizacion   datetime
```

Agregar índice único lógico por:

```txt
sucursal_id + id_local_pos
```

### 12.4 Pedido

Tabla:

```txt
caramelo_pedidos
```

Campos:

```txt
id                    integer primary key
folio                 string unique nullable
sucursal_id            FK a caramelo_sucursales
cliente_nombre         string
cliente_telefono       string nullable
cliente_email          string nullable
total                 numeric(12, 2)
estatus               string default 'pendiente'
notas                 text nullable
fecha_registro         datetime
fecha_modificacion     datetime
```

Estatus sugeridos:

```txt
pendiente
recibido_por_pos
en_preparacion
entregado
cancelado
```

### 12.5 PedidoDetalle

Tabla:

```txt
caramelo_pedido_detalles
```

Campos:

```txt
id                    integer primary key
pedido_id              FK a caramelo_pedidos
producto_id            FK a caramelo_productos nullable
id_local_pos           string nullable
nombre_producto        string
cantidad              numeric(12, 3)
precio_unitario        numeric(12, 2)
subtotal              numeric(12, 2)
```

---

## 13. Endpoints públicos de Caramelo

Estos endpoints serán consumidos por la página web React.

### 13.1 Obtener categorías

```txt
GET /api/caramelo/categorias
```

Debe devolver solo categorías activas.

Query params opcionales:

```txt
sucursal_id
```

Respuesta:

```json
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "nombre": "Dulces"
    }
  ]
}
```

### 13.2 Obtener productos

```txt
GET /api/caramelo/productos
```

Debe devolver solo productos:

```txt
activo = true
visible_web = true
```

Query params:

```txt
sucursal_id
categoria_id
search
page
limit
```

Respuesta paginada:

```json
{
  "ok": true,
  "data": {
    "items": [],
    "page": 1,
    "limit": 24,
    "total": 0,
    "pages": 0
  }
}
```

### 13.3 Obtener detalle de producto

```txt
GET /api/caramelo/productos/<int:producto_id>
```

Debe devolver el detalle público del producto.

### 13.4 Crear pedido web

```txt
POST /api/caramelo/pedidos
```

Payload esperado:

```json
{
  "sucursal_id": "sucursal_001",
  "cliente_nombre": "Juan Pérez",
  "cliente_telefono": "4420000000",
  "cliente_email": "cliente@email.com",
  "notas": "Entregar por la tarde",
  "items": [
    {
      "producto_id": 1,
      "cantidad": 2
    }
  ]
}
```

La API debe calcular precios desde la BD del servidor, no confiar en precios enviados por frontend.

Respuesta:

```json
{
  "ok": true,
  "message": "Pedido registrado",
  "data": {
    "pedido_id": 1,
    "folio": "CAR-000001",
    "status": "pendiente"
  }
}
```

---

## 14. Endpoints de sincronización POS -> API

Estos endpoints requieren API Key.

### 14.1 Sincronizar categorías

```txt
POST /api/caramelo/sync/categorias
```

Headers:

```txt
X-API-Key: <api_key>
```

Payload:

```json
{
  "sucursal_id": "sucursal_001",
  "categorias": [
    {
      "id_local": "CAT001",
      "nombre": "Dulces",
      "activo": true,
      "fecha_modificacion": "2026-05-22 12:30:00"
    }
  ]
}
```

Comportamiento:

- si no existe categoría por `sucursal_id + id_local`, crearla;
- si existe, actualizarla;
- guardar `fecha_sincronizacion` con la fecha actual del servidor.

### 14.2 Sincronizar productos

```txt
POST /api/caramelo/sync/productos
```

Headers:

```txt
X-API-Key: <api_key>
```

Payload:

```json
{
  "sucursal_id": "sucursal_001",
  "productos": [
    {
      "id_local": "P001",
      "categoria_id_local": "CAT001",
      "sku": "DUL-FRESA-001",
      "nombre": "Caramelo de fresa",
      "descripcion": "Caramelo sabor fresa",
      "precio": 15.00,
      "existencia": 24,
      "imagen_url": "https://...",
      "activo": true,
      "visible_web": true,
      "fecha_modificacion": "2026-05-22 12:30:00"
    }
  ]
}
```

Comportamiento:

- upsert por `sucursal_id + id_local`;
- relacionar categoría usando `categoria_id_local`;
- si la categoría no existe, permitir `categoria_id = null` y no fallar todo el lote;
- devolver conteo de creados, actualizados y errores.

Respuesta:

```json
{
  "ok": true,
  "message": "Productos sincronizados",
  "data": {
    "recibidos": 1,
    "creados": 0,
    "actualizados": 1,
    "errores": []
  }
}
```

---

## 15. Endpoints de sincronización API -> POS

Estos endpoints también requieren API Key.

### 15.1 Obtener pedidos pendientes

```txt
GET /api/caramelo/sync/pedidos-pendientes?sucursal_id=sucursal_001
```

Debe devolver pedidos con status:

```txt
pendiente
```

Respuesta:

```json
{
  "ok": true,
  "data": [
    {
      "id": 1,
      "folio": "CAR-000001",
      "cliente_nombre": "Juan Pérez",
      "cliente_telefono": "4420000000",
      "total": 30.00,
      "status": "pendiente",
      "items": [
        {
          "id_local_pos": "P001",
          "nombre_producto": "Caramelo de fresa",
          "cantidad": 2,
          "precio_unitario": 15.00,
          "subtotal": 30.00
        }
      ]
    }
  ]
}
```

### 15.2 Confirmar pedido recibido por POS

```txt
POST /api/caramelo/sync/pedidos/<int:pedido_id>/confirmar-recibido
```

Payload:

```json
{
  "sucursal_id": "sucursal_001"
}
```

Comportamiento:

- validar API Key;
- validar que el pedido pertenezca a la sucursal;
- cambiar status a `recibido_por_pos`.

---

## 16. Módulo Granos como placeholder

Crear módulo base:

```txt
app/modules/granos/
```

Por ahora solo debe tener un endpoint placeholder:

```txt
GET /api/granos/status
```

Respuesta:

```json
{
  "ok": true,
  "message": "Granos module ready",
  "data": {}
}
```

Esto servirá como ejemplo para agregar más proyectos sin mezclar rutas.

---

## 17. Seguridad mínima

Implementar desde el inicio:

1. CORS restringido a dominios permitidos.
2. API Key para endpoints `/sync/*`.
3. No aceptar precios desde frontend al crear pedidos.
4. Validar cantidad mayor a cero.
5. No exponer stack traces en producción.
6. Usar variables de entorno para secretos.
7. Preparar `.env.example`, pero no subir `.env`.
8. Agregar `.gitignore`.

---

## 18. Docker

Crear `Dockerfile` para la API Flask.

Debe ejecutar con Gunicorn:

```txt
gunicorn "app:create_app()" --bind 0.0.0.0:8000
```

Crear `docker-compose.yml` con servicios:

```txt
api
postgres
```

Ejemplo esperado de puertos:

```txt
api: 8000
postgres: 5432 interno
```

El compose debe permitir desarrollo local.

---

## 19. Requirements

Crear `requirements.txt` con dependencias mínimas:

```txt
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-Cors
python-dotenv
gunicorn
psycopg2-binary
marshmallow
```

Si se usa Pydantic en lugar de Marshmallow, documentar la decisión.

---

## 20. README

Crear un `README.md` con:

- descripción del proyecto;
- instalación local;
- variables de entorno;
- comandos para migraciones;
- cómo correr con Flask;
- cómo correr con Docker;
- endpoints principales.

Comandos mínimos esperados:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask db init
flask db migrate -m "initial migration"
flask db upgrade
flask run
```

Para Docker:

```bash
docker compose up --build
```

---

## 21. Criterios de aceptación

El proyecto debe quedar funcional con:

1. `GET /api/health` funcionando.
2. Blueprints separados por módulo.
3. Módulo `caramelo` registrado en `/api/caramelo`.
4. Módulo `granos` registrado en `/api/granos`.
5. Modelos de Caramelo creados.
6. Migraciones configuradas.
7. Endpoint público de productos listo.
8. Endpoint de sincronización de productos protegido por API Key.
9. Endpoint para crear pedidos web.
10. Dockerfile y docker-compose funcionales.
11. `.env.example` incluido.
12. `.gitignore` incluido.
13. Código organizado para poder agregar nuevos proyectos sin modificar todo el core.

---

## 22. Importante sobre mantenibilidad

No poner todas las rutas en un solo archivo gigante.

Evitar esto:

```txt
app.py con todas las rutas de todos los proyectos
```

Preferir esto:

```txt
app/modules/caramelo/routes.py
app/modules/granos/routes.py
app/modules/health/routes.py
```

Si un módulo crece mucho, dividir sus rutas así:

```txt
app/modules/caramelo/routes/
├── __init__.py
├── public.py
├── sync.py
└── admin.py
```

Por ahora puede empezar con un solo `routes.py` por módulo, pero dejar comentarios o estructura preparada para crecer.

---

## 23. Resultado esperado

Codex debe generar el proyecto base completo con archivos reales, no solo pseudocódigo.

La API debe poder ejecutarse localmente y responder:

```txt
GET http://localhost:8000/api/health
```

con:

```json
{
  "ok": true,
  "message": "API running",
  "data": {
    "service": "mechastationlab-api"
  }
}
```

