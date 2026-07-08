# FlavorGraph — Recipe Recommendation System

FlavorGraph is a full-stack **recipe recommendation** web app. You tell it what
ingredients you have and how you feel like eating (quick, vegetarian, spicy, a
dessert…), and it matches recipes for you and explains *why* each one was
chosen. You can also click **"More like this"** on any recipe to explore
neighbours with similar ingredients.

It is built as three separate, containerised services connected over a private
Docker network, and it runs end-to-end with a single command:

```bash
docker compose up --build
```

Then open **http://localhost:8080**.

---

## Why this project

Recommendation and matching systems are everywhere — Netflix suggestions, dating
site matching, "similar image" search. Cooking is a relatable domain where the
matching logic is easy to reason about and easy to *explain*: two recipes are
similar when they share ingredients and tags, and a recipe is a good match when
its ingredients and tags overlap with what you asked for.

What makes this implementation interesting:

- **Explainable results.** Every recommendation comes with human-readable
  reasons ("Uses chicken, garlic", "Highly rated (4.6 stars)", "Quick to make")
  instead of an opaque score.
- **Three blended signals.** It combines classic *content-based* matching
  (TF-IDF over ingredients + tags), a *graph* view of how recipes connect
  through shared ingredients (NetworkX), and *popularity/quality* from real user
  ratings.
- **Runs anywhere.** The core engine is CPU-only and dependency-light, so
  `docker compose up` works on any laptop with no GPU and no external services.
- **An optional quantum demo.** A self-contained, disabled-by-default module
  shows how a quantum optimiser (QAOA via Qiskit) could re-rank results for
  *diversity*. It never affects the core app and is only reachable when
  explicitly enabled.

---

## Architecture

```
                Browser (http://localhost:8080)
                        │
                        ▼
        ┌───────────────────────────────┐
        │  frontend  (React + Vite)      │   nginx serves the built SPA and
        │  container: nginx              │   proxies /api/* to the backend
        └───────────────┬───────────────┘
                        │  /api  →  http://backend:8000
                        ▼
        ┌───────────────────────────────┐
        │  backend  (FastAPI, Python)    │
        │                                │
        │  routes → services → repos     │
        │                    │           │
        │      recommender engine        │
        │   ├── content_based (TF-IDF)   │
        │   ├── graph_engine (NetworkX)  │
        │   ├── ratings (popularity)     │
        │   └── quantum_demo (optional)  │
        └───────────────┬───────────────┘
                        │  SQLAlchemy
                        ▼
        ┌───────────────────────────────┐
        │  db  (PostgreSQL)              │
        └───────────────────────────────┘
```

All three run on a private bridge network (`flavorgraph_net`). The frontend and
backend are logically separated in their own containers and talk only through
the HTTP API, as required.

See [`docs/architecture.md`](docs/architecture.md) for a deeper walkthrough.

---

## Tech stack

| Layer            | Technology                                            |
|------------------|-------------------------------------------------------|
| Frontend         | React 18 + Vite (plain JavaScript, no jQuery)         |
| Reverse proxy    | nginx (serves the SPA, proxies `/api`)                |
| Backend / API    | FastAPI (Python 3.12)                                  |
| ORM              | SQLAlchemy 2                                           |
| Database         | PostgreSQL 16                                          |
| Recommender      | scikit-learn (TF-IDF), NetworkX (graph), NumPy        |
| Optional quantum | Qiskit + qiskit-optimization (QAOA) — off by default  |
| Orchestration    | Docker + Docker Compose                               |

---

## Quick start

Requirements: **Docker** and **Docker Compose** (Docker Desktop covers both).

```bash
git clone https://github.com/kdivyanshu5/recipe-recommendation-system.git
cd recipe-recommendation-system
docker compose up --build
```

On startup the backend waits for PostgreSQL, creates the tables, and
automatically seeds the bundled **sample dataset** (50 recipes + ratings) so the
app is usable immediately.

- Frontend UI: **http://localhost:8080**
- API docs (Swagger): **http://localhost:8000/docs**
- Health check: **http://localhost:8000/health**

To stop and remove everything:

```bash
docker compose down          # keep the database volume
docker compose down -v       # also wipe the database
```

---

## Using the app

1. Type ingredients you have, e.g. `chicken, garlic, rice`.
2. Tap the mood chips (vegetarian, quick, dinner…).
3. Optionally set ingredients to avoid, a max cooking time, or a minimum rating.
4. Press **Find recipes** — results are ranked and annotated with reasons.
5. Click **More like this** on a card to explore similar recipes.

---

## API overview

| Method | Path                          | Description                              |
|--------|-------------------------------|------------------------------------------|
| GET    | `/health`                     | Service + DB status, recipe count        |
| GET    | `/recipes/`                   | Paginated list of recipes                |
| GET    | `/recipes/search?q=`          | Search recipes by name                   |
| GET    | `/recipes/{id}`               | Full recipe detail                       |
| POST   | `/recommend/`                 | Recommend by preferences (main feature)  |
| GET    | `/recommend/popular`          | Most popular recipes                     |
| GET    | `/recommend/similar/{id}`     | "More like this"                         |
| POST   | `/recommend/quantum`          | Optional QAOA diversity demo (503 if off)|
| POST   | `/admin/rebuild`              | Rebuild the engine after loading data    |

Example recommendation request:

```bash
curl -X POST http://localhost:8000/recommend/ \
  -H "Content-Type: application/json" \
  -d '{"ingredients":["chicken","garlic"],"tags":["dinner"],"max_minutes":60,"limit":5}'
```

Full request/response details are in [`docs/api.md`](docs/api.md).

---

## The dataset

**Source (declared):** [Food.com Recipes and User Interactions](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions)
(`RAW_recipes.csv`, `RAW_interactions.csv`).

Because the full dataset is ~900 MB and slow to import, the repository ships a
small, deterministic **sample** in [`data/`](data/) that keeps the exact same
column layout. This is what makes the project plug-and-play.

- **Sample (default):** `data/recipes_sample.csv` and
  `data/interactions_sample.csv` are seeded automatically on first startup.
  They are regenerated with `python backend/scripts/generate_sample_data.py`.
- **Full dataset (optional):** download the two RAW CSVs from Kaggle into a
  `dataset/` folder, then run the loader (see below).

Load the full data into the running database:

```bash
# From the host, pointing at the Dockerised DB:
DB_HOST=localhost pip install -r backend/requirements.txt
DB_HOST=localhost python backend/scripts/load_full_dataset.py \
  --recipes dataset/RAW_recipes.csv \
  --interactions dataset/RAW_interactions.csv \
  --limit-recipes 20000
# Then refresh the in-memory engine without a restart:
curl -X POST http://localhost:8000/admin/rebuild
```

More detail in [`docs/data_preparation.md`](docs/data_preparation.md) and
[`docs/database.md`](docs/database.md).

---

## How the recommender works

1. **Content match** — each recipe becomes a short "document" of its ingredients
   and tags. A TF-IDF vector space is fitted over all recipes; your preferences
   are vectorised the same way and compared with cosine similarity.
2. **Graph** — recipes are nodes in a NetworkX graph, connected when they share
   ingredients (edge weight = number shared). This powers "more like this".
3. **Popularity** — average rating from the interactions table nudges the
   ranking toward recipes people actually liked.

The final preference score is `0.75 × content + 0.25 × rating`. Hard filters
(max time, min rating, excluded ingredients) are applied before ranking. The
engine is fitted once and cached in memory (rebuild with `/admin/rebuild`).

---

## Optional: the quantum demo

Disabled by default. It frames "pick a diverse short-list from the top
candidates" as a small QUBO and solves it with **QAOA** (Qiskit).

```bash
# 1. install the extra dependencies
pip install -r backend/requirements-quantum.txt
# 2. enable it and restart
ENABLE_QUANTUM=true docker compose up --build
# 3. call it
curl -X POST http://localhost:8000/recommend/quantum \
  -H "Content-Type: application/json" -d '{"tags":["dinner"],"limit":4}'
```

If it is disabled or Qiskit is missing, the endpoint returns a friendly `503`
with instructions — the rest of the app is unaffected.

---

## Running tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

`tests/test_parsing.py` covers the data parsing helpers; `tests/test_recommender.py`
covers ranking, filtering, similarity and popularity on a small fixture dataset.

---

## Project structure

```
recipe-recommendation-system/
├── docker-compose.yml          # orchestrates db + backend + frontend
├── .env.example                # optional overrides
├── data/                       # bundled sample dataset (auto-seeded)
├── docs/                       # architecture, api, database, data prep
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-quantum.txt
│   ├── scripts/                # sample generator + full-dataset loader
│   ├── tests/
│   └── app/
│       ├── main.py             # FastAPI app + startup seeding
│       ├── config.py           # env-driven settings
│       ├── database/           # engine + session
│       ├── models/             # SQLAlchemy models
│       ├── schemas/            # Pydantic schemas
│       ├── repositories/       # data-access layer
│       ├── services/           # business logic
│       ├── routes/             # HTTP endpoints
│       ├── recommender/        # content, graph, ratings, quantum, engine
│       └── utils/              # parsing + seeding helpers
└── frontend/
    ├── Dockerfile              # Vite build → nginx
    ├── nginx.conf              # serves SPA, proxies /api
    └── src/                    # React app + components
```

---

