# API del CMS

API del CMS para el flujo de automatización de blogs. Python + FastAPI + PostgreSQL, organizada en cuatro capas.

## Capas

```
Petición HTTP → controllers → services → repositories → PostgreSQL
                                  └──→ clients → Builder / API de métricas
```

| Capa | Carpeta | Responsabilidad |
|---|---|---|
| Controllers | `app/controllers/` | Routers de FastAPI: reciben la petición y devuelven la respuesta. Sin lógica de negocio. |
| Services | `app/services/` | Reglas de negocio (404 si no existe, 409 si el slug se repite, armar el contenido para el Builder). |
| Repository | `app/repositories/` | Único lugar con consultas a la base de datos. |
| Models | `app/models/` | `entities.py` (tablas SQLAlchemy) y `schemas.py` (validación Pydantic). |

`app/clients/` no es una capa: son los clientes HTTP que usan los services para hablar con el Builder y con la API de métricas.

## Puesta en marcha

```bash
docker compose up -d                    # PostgreSQL local (usuario, contraseña y base: cms)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head                    # crea las tablas
uvicorn app.main:app --reload
```

Documentación interactiva: http://localhost:8000/docs

## Endpoints

| Método y ruta | Qué hace |
|---|---|
| `GET/POST /api/blogs` · `GET/PUT/DELETE /api/blogs/{id}` | Blogs |
| `GET/POST /api/blogs/{id}/posts` · `GET/PUT/DELETE /api/posts/{id}` | Artículos (`?include_drafts=false` oculta borradores) |
| `GET/POST /api/blogs/{id}/projects` · `GET/PUT/DELETE /api/projects/{id}` | Proyectos |
| `GET/PUT/DELETE /api/blogs/{id}/landing` | Landing completa (el `PUT` crea o reemplaza todo, incluidas sus listas) |
| `POST /api/build` con `{"blogId": 1}` | Arma el contenido, se lo manda al Builder y guarda el resultado |
| `GET /api/build/{id}` · `GET /api/blogs/{id}/builds` | Historial de generaciones |
| `GET /api/metrics/{blogId}` | Consulta las métricas por GraphQL |

"Subir" a Vercel **no** pasa por el CMS: según el documento del maestro, lo hace la interfaz.

## Builder y API de métricas

Con `USE_MOCKS=true` (valor por defecto) ambos se simulan y **no generan sitios ni analíticas reales**. Cuando existan, pon `USE_MOCKS=false` y ajusta `BUILDER_URL` y `METRICS_URL` en `.env`.

- **Builder:** el CMS hace `POST {BUILDER_URL}/build` con este JSON: `{ "blog": {...}, "posts": [...], "projects": [...], "landing": {...} }`. Los `posts` incluyen los borradores con su campo `draft`; el Builder decide si los omite. Debe responder con un JSON (se guarda en la tabla `builds`).
- **Métricas:** el CMS hace `POST {METRICS_URL}` con esta consulta GraphQL y espera `data.metricas.visitas` y `data.metricas.visitantesUnicos`:

```graphql
query Metricas($blogId: Int!) {
  metricas(blogId: $blogId) { visitas visitantesUnicos }
}
```

## Validaciones que replican a tu blog en Astro

- `description` del artículo: máximo 160 caracteres (si se pasa, `astro build` falla).
- `slug`: minúsculas, números y guiones; único dentro de cada blog.

## Pruebas

```bash
pytest
```

Las pruebas usan SQLite en memoria; la API real usa PostgreSQL. La migración de Alembic se comparó contra las tablas de los modelos en dialecto PostgreSQL, pero no se ha ejecutado contra una instancia real de PostgreSQL.

## Pendiente antes de desplegar

- Restringir los orígenes de CORS en `app/main.py` (ahora acepta cualquiera).
- No hay login ni usuarios, tal como pide el proyecto.
