# Architecture

NeuroHub is a modular Flask API.

```mermaid
flowchart TD
    Client[Web client] --> API[Flask API]
    POS[POS integration] --> API
    API --> Health[Health blueprint]
    API --> Caramelo[Caramelo blueprint]
    API --> Granos[Granos placeholder]
    Caramelo --> ORM[SQLAlchemy]
    ORM --> DB[(PostgreSQL)]
```

The application factory initializes extensions and registers blueprints. Alembic manages schema migrations. Tests can use SQLite; PostgreSQL integration tests remain necessary for database-specific behavior.

## Deployment checklist

- Explicitly set FLASK_ENV=production.
- Supply a strong SECRET_KEY and API_KEY through environment variables.
- Restrict CORS_ORIGINS to trusted clients.
- Use HTTPS and restrict database network access.
- Apply existing migrations with flask --app app:create_app db upgrade.
- Run python -m pytest before deployment.
- Review dependency audit results in CI.
- Review per-branch authorization and API key rotation before exposing synchronization endpoints.
