# How to install

This guide gets FlavorGraph running on your machine. The normal way is Docker —
one command and everything comes up with the built-in sample data. Loading the
full Food.com dataset is optional and covered further down as a separate part.

A note on terminals before you start: every command in this guide goes into the
**VS Code terminal**. Open the project folder in VS Code, then go to
Terminal → New Terminal. You never need the Docker Desktop terminal or a
terminal inside a container. On Windows the VS Code terminal is PowerShell, and
the commands below are written for it. Where Mac/Linux is different, both
versions are shown.

---

## Part 1 — Run the app with sample data (the default)

### 1. Install Docker

Get Docker Desktop from https://www.docker.com/products/docker-desktop/ (it
includes Docker Compose). Start it and wait until it says "running", then check
in the VS Code terminal:

```powershell
docker --version
docker compose version
```

It's also worth upgrading pip once so you don't hit version conflicts later:

```powershell
python -m pip install --upgrade pip
```

### 2. Get the code

```powershell
git clone https://github.com/kdivyanshu5/recipe-recommendation-system.git
cd recipe-recommendation-system
```

Or download the ZIP, extract it, and open that folder in VS Code.

### 3. Start it

```powershell
docker compose up --build
```

This starts three containers: the database (port 5432), the backend
(http://localhost:8000) and the frontend (http://localhost:8080).

The first time it runs, the backend creates the tables and loads the sample
dataset (50 recipes with ratings) by itself. That's the `AUTO_SEED: "true"`
setting in `docker-compose.yml`, which is on by default — you don't have to do
anything. The app is ready to use as soon as the containers are up.

### 4. Check it works

- App: http://localhost:8080
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health — should show `"recipes": 50`

### 5. Stopping

Press Ctrl+C in the terminal, then:

```powershell
docker compose down       # stop, keep the database
docker compose down -v    # stop and wipe the database too
```

### Changing settings (optional)

The defaults just work. If you want different database credentials, copy
`.env.example` to `.env` and edit it:

```powershell
copy .env.example .env    # Mac/Linux: cp .env.example .env
```

The variables are `DB_USER`, `DB_PASSWORD`, `DB_NAME` and `ENABLE_QUANTUM`.

---

## Part 2 — Switching to the full dataset (optional)

The sample is the default and is enough for demos and grading. Only do this part
if you want the app running on the real Food.com data. It takes a few extra
steps because the files are huge (~350 MB for the ratings alone).

All commands go in the VS Code terminal, from the project root (the folder with
`docker-compose.yml` in it).

### Step 1 — Download the data

Get the dataset from Kaggle (free account needed):
https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions

Extract the ZIP. You only need two files out of it: `RAW_recipes.csv` and
`RAW_interactions.csv`.

### Step 2 — Make a `dataset` folder

The project already has a `data/` folder — that one holds the small sample,
leave it alone. Make a separate folder for the big files (it's in `.gitignore`,
so they never end up on GitHub):

```powershell
mkdir dataset
```

Move the two CSVs into it and confirm they're there:

```powershell
dir dataset      # Mac/Linux: ls dataset
```

### Step 3 — Two edits in `docker-compose.yml`

Open `docker-compose.yml` in VS Code and check these:

First, the `db` service must publish its port so the loader script (which runs
on your PC) can reach the database. Under `db:` there should be:

```yaml
    ports:
      - "5432:5432"
```

If it's missing, add it, lined up with `environment:` and `volumes:`.

Second, turn auto-seeding off **for now**, so the sample recipes don't get mixed
in with the real ones. Under `backend:` → `environment:` change:

```yaml
      AUTO_SEED: "false"
```

This is temporary — "true" stays the project default, and Step 8 below shows how
to switch back to the sample later.

### Step 4 — Start with an empty database

The sample and the real dataset can use overlapping recipe IDs, so wipe the
database first:

```powershell
docker compose down -v
docker compose up --build -d
```

The `-v` deletes the old data. The `-d` runs everything in the background so you
keep your terminal. Give it about 15 seconds to come up.

### Step 5 — Install the Python packages on your PC

The loader script runs on your PC, not inside Docker, so it needs the backend
packages locally. If you have the project's virtual environment, activate it
first:

```powershell
backend\.venv\Scripts\activate    # Mac/Linux: source backend/.venv/bin/activate
```

Then:

```powershell
pip install -r backend/requirements.txt
```

### Step 6 — Run the loader (once only)

On Windows, set the variable on its own line and keep the command on one line:

```powershell
$env:DB_HOST = "localhost"
python backend/scripts/load_full_dataset.py --recipes dataset/RAW_recipes.csv --interactions dataset/RAW_interactions.csv --limit-recipes 20000
```

On Mac/Linux:

```bash
DB_HOST=localhost python backend/scripts/load_full_dataset.py \
  --recipes dataset/RAW_recipes.csv \
  --interactions dataset/RAW_interactions.csv \
  --limit-recipes 20000
```

It takes a few minutes. When it's done you'll see:

```
Imported 20000 recipes.
Imported interactions for the loaded recipes.
Done. Restart the backend or call POST /admin/rebuild to refresh the engine.
```

Run it once only — running it again inserts duplicate ratings. If you need a
do-over, go back to Step 4 first. And keep `--limit-recipes 20000`: it's plenty,
and loading all 230k recipes makes the engine slow to build and heavy on memory.

### Step 7 — Rebuild the recommender

The backend keeps its recommendation engine in memory, so tell it to rebuild
from the new data. The first build over 20k recipes takes a minute or two, which
is why the timeout is generous.

On Windows — and note, don't use `curl -X POST` in PowerShell, its `curl` is a
different command and it fails:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/admin/rebuild -TimeoutSec 600
```

On Mac/Linux:

```bash
curl -X POST --max-time 600 http://localhost:8000/admin/rebuild
```

You should get back `status: rebuilt` with the recipe count. Check
http://localhost:8000/health — it should now say `"recipes": 20000`. Refresh
http://localhost:8080 and search.

### Step 8 — Going back to the sample (if you want)

Set `AUTO_SEED: "true"` again in `docker-compose.yml`, then:

```powershell
docker compose down -v
docker compose up --build -d
```

The sample reseeds itself on startup and you're back to the default setup.

### If something goes wrong

- `Connection refused` on port 5432 — the db port isn't published (Step 3), the
  stack isn't running, or you forgot `$env:DB_HOST = "localhost"`.
- `duplicate key value violates unique constraint` — sample data is still in
  the database, or the loader ran twice. Redo Step 4, then Step 6 once.
- `DB_HOST=localhost : The term ... is not recognized` — that's the Mac/Linux
  syntax. On Windows use the two-line version in Step 6.
- The rebuild call dies with "response ended prematurely" — the backend probably
  ran out of memory building the graph. Check
  `docker compose logs backend --tail=30`, give Docker Desktop more memory
  (Settings → Resources), or lower `--limit-recipes`.
- `FileNotFoundError: dataset/RAW_recipes.csv` — you're not in the project root,
  or the files aren't in `dataset/` (Step 2).

---

## Part 3 — The quantum demo (optional)

Off by default, and the app doesn't need it. It adds one extra endpoint that
re-ranks results for diversity using QAOA (Qiskit). Turning it on takes two
edits and a rebuild:

1. The quantum packages have to be installed *inside the backend container* —
   installing them with pip on your PC does nothing for the container. Open
   `backend/Dockerfile` and add this line right after `COPY . .`:

```dockerfile
RUN pip install --no-cache-dir -r requirements-quantum.txt
```

2. In `docker-compose.yml`, under `backend:` → `environment:`, set:

```yaml
      ENABLE_QUANTUM: "true"
```

3. Rebuild:

```powershell
docker compose up --build -d
```

Try it on Windows:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/recommend/quantum -ContentType "application/json" -Body '{"tags":["dinner"],"limit":4}'
```

Or on Mac/Linux:

```bash
curl -X POST http://localhost:8000/recommend/quantum \
  -H "Content-Type: application/json" -d '{"tags":["dinner"],"limit":4}'
```

If it's disabled or Qiskit isn't installed, the endpoint just answers with a 503
and an explanation — nothing else in the app is affected. To turn it off again,
set `ENABLE_QUANTUM: "false"` and run `docker compose up -d`.

---

## Part 4 — Running without Docker (for development)

You still need the database, so start just that container:

```powershell
docker compose up db
```

Backend, in a second VS Code terminal:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate            # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Windows:
$env:DB_HOST = "localhost"
uvicorn app.main:app --reload --port 8000
# Mac/Linux:  DB_HOST=localhost uvicorn app.main:app --reload --port 8000
```

Frontend, in a third terminal:

```powershell
cd frontend
npm install
npm run dev
```

The dev frontend runs at http://localhost:5173 and forwards `/api` calls to the
backend on port 8000.

---

## General troubleshooting

- Port already in use — something else has 8080, 8000 or 5432. Stop it or change
  the mappings in `docker-compose.yml`.
- `error during connect ... dockerDesktopLinuxEngine` — Docker Desktop isn't
  running yet. Open it, wait, retry.
- Backend can't reach the database at startup — it retries on its own while
  Postgres boots. Wait a few seconds; check `docker compose logs backend`.
- UI loads but shows an error — check http://localhost:8000/health first.
- Start completely fresh — `docker compose down -v` then
  `docker compose up --build`.
