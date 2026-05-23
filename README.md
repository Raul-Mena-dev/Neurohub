# NeuroHub

API central en Flask para NeuroHub. El proyecto esta preparado para servir varios modulos bajo `/api`, empezando con Caramelo y un placeholder de Granos.

## Stack

- Python 3.11+
- Flask
- Flask-SQLAlchemy
- Flask-Migrate / Alembic
- Flask-CORS
- PostgreSQL
- Gunicorn

## Instalacion local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

En Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

## Variables de entorno

```env
FLASK_ENV=development
SERVICE_NAME=neurohub
SECRET_KEY=change_me
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/neurohub_api
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://mechastationlab.com,https://caramelo.mechastationlab.com
API_KEY_HEADER=X-API-Key
API_KEY=change_me_api_key
```

`API_KEY` permite proteger rapidamente los endpoints de sincronizacion. La estructura tambien soporta validar contra `caramelo_sucursales.api_key_hash` usando `sucursal_id`.

## Migraciones

```bash
flask --app app:create_app db init
flask --app app:create_app db migrate -m "initial migration"
flask --app app:create_app db upgrade
```

## Ejecutar la API

```bash
flask --app app:create_app run --host 0.0.0.0 --port 8000
```

Tambien se puede ejecutar:

```bash
python run.py
```

Health check:

```txt
GET http://localhost:8000/api/health
```

Respuesta esperada:

```json
{
  "ok": true,
  "message": "API running",
  "data": {
    "service": "neurohub"
  }
}
```

## Docker

```bash
docker compose up --build
```

La API queda disponible en:

```txt
http://localhost:8000
```

## Endpoints principales

### Health

- `GET /api/health`

### Caramelo publico

- `GET /api/caramelo/categorias`
- `GET /api/caramelo/productos`
- `GET /api/caramelo/productos/<producto_id>`
- `POST /api/caramelo/pedidos`

### Caramelo sincronizacion POS

Estos endpoints requieren el header configurado en `API_KEY_HEADER`, por defecto:

```txt
X-API-Key: change_me_api_key
```

- `POST /api/caramelo/sync/categorias`
- `POST /api/caramelo/sync/productos`
- `GET /api/caramelo/sync/pedidos-pendientes?sucursal_id=sucursal_001`
- `POST /api/caramelo/sync/pedidos/<pedido_id>/confirmar-recibido`

### Granos

- `GET /api/granos/status`

## Estructura

```txt
app/
  common/
  modules/
    health/
    caramelo/
    granos/
```

Cada proyecto debe crecer dentro de `app/modules/<nombre_proyecto>/` con sus rutas, modelos, esquemas y servicios.
