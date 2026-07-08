# How to Install

This guide walks you through getting FlavorGraph running on your machine. The
recommended path uses Docker and needs just one command. A manual path (running
each part yourself) is included at the end for development.

---

## Option A — Docker (recommended, plug and play)

### 1. Prerequisites

Install **Docker Desktop**, which includes both Docker and Docker Compose:

- Windows / macOS: <https://www.docker.com/products/docker-desktop/>
- Linux: install `docker` and the `docker compose` plugin from your package manager.

Verify the install:

```bash
docker --version
docker compose version
```

### 2. Get the code

```bash
git clone https://github.com/kdivyanshu5/recipe-recommendation-system.git
cd recipe-recommendation-system
```

(Or download the ZIP, extract it, and `cd` into the folder.)

### 3. Start everything

```bash
docker compose up --build
```

This builds the images and starts three containers:

| Service    | What it is                        | URL / Port                    |
|------------|-----------------------------------|-------------------------------|
| `db`       | PostgreSQL database                | localhost:5432                |
| `backend`  | FastAPI recommendation API         | http://localhost:8000         |
| `frontend` | React app served by nginx          | http://localhost:8080         |

On first startup the backend waits for the database, creates the tables, and
automatically loads the bundled **sample dataset** (50 recipes + ratings), so the
app is ready to use right away.

### 4. Open the app

- **Web UI:** <http://localhost:8080>
- **API docs (Swagger):** <http://localhost:8000/docs>
- **Health check:** <http://localhost:8000/health> — should show
  `{"status": "ok", "recipes": 50, ...}`

### 5. Stop it

```bash
# In the terminal running compose, press Ctrl+C, then:
docker compose down        # stop and remove containers (keeps the data volume)
docker compose down -v     # also wipe the database volume
```

---

## Configuration (optional)

Everything works with zero configuration. To override defaults, copy the example
env file and edit it:

```bash
cp .env.example .env
```

| Variable        | Default      | Purpose                                   |
|-----------------|--------------|-------------------------------------------|
| `DB_USER`       | `postgres`   | Database user                             |
| `DB_PASSWORD`   | `password`   | Database password                         |
| `DB_NAME`       | `recipe_db`  | Database name                             |
| `ENABLE_QUANTUM`| `false`      | Turn on the optional QAOA demo endpoint   |

---

## Loading the full dataset (optional)

The app ships with a sample so it runs instantly. To use the complete Food.com
data instead:

1. Download `RAW_recipes.csv` and `RAW_interactions.csv` from
   [Kaggle](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions).
2. Put them in a `data/` folder at the repo root (this folder is gitignored).
3. Rename them with "RAW_recipes.csv -> recipes_sample.csv" and "RAW_interactions.csv -> interactions_sample.csv".
4. Remove container and re-run :
```bash
docker compose up --build
```



## Enabling the optional quantum demo

Disabled by default because it is heavy and not needed for the core app.

```bash
pip install -r backend/requirements-quantum.txt
ENABLE_QUANTUM=true docker compose up --build
```

The `POST /recommend/quantum` endpoint then re-ranks results for diversity using
QAOA (Qiskit). If it is disabled or Qiskit is missing, that endpoint simply
returns a friendly `503` and the rest of the app is unaffected.

---

## Option B — Manual setup (for development)

Run the pieces yourself without the frontend/backend containers. You still need a
PostgreSQL database — the easiest is to start just the db container:

```bash
docker compose up db
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Point at the local database and run the API with autoreload
DB_HOST=localhost uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite serves the app at <http://localhost:5173> and proxies `/api` to the backend
at `localhost:8000`.

---

## Troubleshooting

- **Port already in use** — something else is using 8080, 8000, or 5432. Stop it,
  or change the host port mappings in `docker-compose.yml`.
- **Backend can't reach the database** — the backend retries automatically while
  Postgres starts. Give it a few seconds; check logs with
  `docker compose logs backend`.
- **UI loads but shows an error** — confirm the backend is healthy at
  <http://localhost:8000/health>.
- **Rebuild from scratch** — `docker compose down -v` then
  `docker compose up --build`.
- **Check logs for any service** — `docker compose logs -f backend`
  (or `frontend` / `db`).
