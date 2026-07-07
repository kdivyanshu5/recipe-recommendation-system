# Architecture

FlavorGraph is split into three containers that each do one job and communicate
only over the network. This keeps the frontend, backend and database logically
separated, as required by the brief.

## Containers

| Container            | Image base        | Responsibility                                  | Exposed port |
|----------------------|-------------------|-------------------------------------------------|--------------|
| `flavorgraph_db`     | `postgres:16`     | Stores recipes and interactions                 | 5432         |
| `flavorgraph_backend`| `python:3.12`     | REST API + recommendation engine                | 8000         |
| `flavorgraph_frontend`| `nginx:1.27`     | Serves the React SPA, proxies `/api` to backend | 80 → 8080    |

They share a private bridge network `flavorgraph_net`. The browser only ever
talks to the frontend; the frontend's nginx forwards `/api/*` to the backend, so
there are no CORS problems and no hard-coded backend hostnames in the browser.

## Backend layers

The backend follows a clean layered design so responsibilities stay separated:

```
routes/         HTTP endpoints (FastAPI routers). No business logic.
   │
services/       Business logic. Orchestrates repositories + the engine.
   │
repositories/   Data access. All SQLAlchemy queries live here.
   │
models/         SQLAlchemy ORM models (tables).
```

Cross-cutting pieces:

- `schemas/` — Pydantic models that validate requests and shape responses.
- `recommender/` — the recommendation engine, independent of the web layer:
  - `content_based.py` — TF-IDF vector space + cosine similarity.
  - `graph_engine.py` — NetworkX ingredient graph.
  - `engine.py` — blends content, graph and ratings; applies filters.
  - `store.py` — caches the fitted engine in memory.
  - `quantum_demo.py` — optional QAOA re-ranking (disabled by default).
- `utils/` — parsing helpers and the CSV seeder.
- `config.py` — all settings, read from environment variables.

## Request lifecycle (a recommendation)

1. Browser POSTs preferences to `/api/recommend/`.
2. nginx forwards to `http://backend:8000/recommend/`.
3. The route validates the body into a `RecommendationRequest`.
4. `RecommendationService` asks `store.get_engine(db)` for the cached engine
   (building it from the database on first use).
5. The engine scores every recipe, applies filters, and returns ranked rows.
6. The service maps rows to `ScoredRecipe` schemas and returns JSON.

## Startup sequence

1. `db` starts and reports healthy via `pg_isready`.
2. `backend` starts (Compose waits for the healthy db), creates tables, and
   seeds the sample CSVs if the tables are empty.
3. `frontend` builds the SPA and serves it through nginx.

## Why these choices

- **nginx proxy** avoids CORS and keeps the API origin stable in every
  environment.
- **In-memory engine cache** avoids re-fitting TF-IDF on every request while
  staying simple (no extra service). `/admin/rebuild` refreshes it after a data
  load.
- **CPU-only core** guarantees the "one command" promise on any machine.
