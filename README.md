# d2-project-backend

FastAPI service behind the Study Progress Analysis (SPA) system. It ingests
exam data files, stores them in PostgreSQL and serves the analytics the client
renders.

The React client lives in a separate repository,
[`d2-project-client`](https://gitlab.gwdg.de/sudarshan.bashyal/d2-project-client).
The two communicate only over this HTTP API.

## System architecture

| Layer | Technology | Repository |
| :--- | :--- | :--- |
| Client | React SPA, Material-UI, AG Grid, Recharts | `d2-project-client` |
| API | FastAPI, Pydantic, SQLAlchemy | `d2-project-backend` (this one) |
| Database | PostgreSQL 15 | provisioned by compose |
| Orchestration | Docker Compose over the published images | `docker-compose/` |

## Layout

```
main.py            app creation, CORS, router mounting, startup seeding
config.py          every environment variable the service reads
dependencies.py    shared FastAPI dependencies (bearer-token auth)
database.py        SQLAlchemy engine, session factory, get_db dependency
models.py          ORM models
schemas.py         Pydantic request/response schemas
seed.py            demonstration data for an empty database
routers/           endpoints grouped by resource
  students.py      roster, profiles, transcripts, status
  courses.py       catalogue, creation, editing, archiving
  grades.py        exam results
  upload.py        CSV/Excel ingestion (preview and confirm)
  stats.py         dashboard KPIs
tests/             pytest suite; tests/smoke/ holds manual scripts
docs/              traceability matrix
```

## Running it

### With Docker (PostgreSQL included)

```bash
docker compose up --build
```

The API is then on `http://localhost:8000`, with interactive documentation at
`http://localhost:8000/docs`.

This compose file starts the database and the API only. To run the whole
system, including the client, use the compose file in the sibling
`docker-compose/` directory, which pulls both published images.

### Without Docker

Requires a reachable PostgreSQL instance, or set `DATABASE_URL` to a SQLite
path for a quick look.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Configuration

All settings are read in `config.py` and every one has a working default.
Copy `.env.example` to `.env` to override them.

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://spa_user:spa_password@db/spa_db` | SQLAlchemy connection URL |
| `API_TOKEN` | `sse-staff-token` | Bearer token required on mutating endpoints |
| `CORS_ORIGINS` | `*` | Comma-separated allow-list |
| `SEED_ON_STARTUP` | `true` | Seed demonstration data into an empty database |

`API_TOKEN` must match the client's `VITE_API_TOKEN`.

## Tests

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

`tests/conftest.py` points the suite at SQLite and disables seeding, so no
PostgreSQL instance is needed.

`tests/smoke/` holds manual scripts that issue real HTTP requests against a
running server. They are intentionally not named `test_*.py` so pytest does not
execute them during collection; see `tests/smoke/README.md`.

## Authentication

Mutating endpoints depend on `verify_token` from `dependencies.py`, which
requires the header:

```
Authorization: Bearer <API_TOKEN>
```

Read endpoints are open.

## Documentation

`docs/TRACEABILITY.md` maps the User Stories and Acceptance Criteria to the
code that implements them, across both repositories.
