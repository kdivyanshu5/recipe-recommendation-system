# Data preparation

## Where the data comes from

Food.com Recipes and User Interactions, from Kaggle:
https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions

Two files are used:

- `RAW_recipes.csv` — the recipes themselves (name, minutes, tags, ingredients, steps).
- `RAW_interactions.csv` — user ratings and reviews.

The dataset comes from the paper "Generating Personalized Recipes from
Historical User Preferences" (Majumder et al., EMNLP 2019).

## The default: a bundled sample

The real interactions file alone is around 350 MB (1.1 million rows), and the
whole dataset is close to 900 MB. Forcing everyone to download and import that
before the app even starts would kill the "runs with one command" idea.

So the project ships with a small sample in `data/` instead — 50 recipes plus
ratings, in exactly the same column layout as the real files. On the first
`docker compose up`, the backend sees an empty database and loads this sample by
itself (that's the `AUTO_SEED: "true"` setting, on by default). Nothing to
configure, nothing to download. Because the sample has the same shape as the
real data, the exact same parsing and loading code handles both.

## Regenerating the sample

The sample is created by a small script — no downloads needed. VS Code terminal:

```powershell
python backend/scripts/generate_sample_data.py
# writes data/recipes_sample.csv and data/interactions_sample.csv
```

It builds 50 familiar recipes across different cuisines with sensible
ingredients, tags, times and nutrition values, plus made-up user ratings so the
popularity signal has something to work with. The random seed is fixed, so the
output is the same every time.

## Secondary option: importing the full dataset

If you want the app running on the real data, there's a loader script for that.
The full step-by-step walkthrough (with the Windows commands, the compose
settings to check first, and fixes for common errors) is in
**How to install.md → Part 2**. In short:

1. Download the two RAW CSVs from Kaggle into a new `dataset/` folder at the
   project root. Don't put them in `data/` — that's the sample's folder, and
   `dataset/` is gitignored so the big files stay off GitHub.
2. In `docker-compose.yml`: the `db` service needs `ports: ["5432:5432"]` so the
   loader on your PC can reach it, and set `AUTO_SEED: "false"` temporarily so
   sample rows don't mix with the real ones.
3. Start from an empty database: `docker compose down -v`, then
   `docker compose up --build -d`.
4. Install the packages locally: `pip install -r backend/requirements.txt`.
5. Run the loader once, in the VS Code terminal.

   Windows (PowerShell):

   ```powershell
   $env:DB_HOST = "localhost"
   python backend/scripts/load_full_dataset.py --recipes dataset/RAW_recipes.csv --interactions dataset/RAW_interactions.csv --limit-recipes 20000
   ```

   Mac/Linux:

   ```bash
   DB_HOST=localhost python backend/scripts/load_full_dataset.py \
     --recipes dataset/RAW_recipes.csv \
     --interactions dataset/RAW_interactions.csv \
     --limit-recipes 20000
   ```

6. Ask the backend to rebuild its in-memory engine. The first build over 20k
   recipes takes a minute or two, hence the long timeout.

   Windows (PowerShell):

   ```powershell
   Invoke-RestMethod -Method Post -Uri http://localhost:8000/admin/rebuild -TimeoutSec 600
   ```

   Mac/Linux:

   ```bash
   curl -X POST --max-time 600 http://localhost:8000/admin/rebuild
   ```

A few things worth knowing: `--limit-recipes 20000` keeps the import and the
engine build manageable (you can drop it, but it gets slow and memory-hungry);
ratings that point at recipes outside the imported set are skipped so nothing
dangles; and running the loader twice duplicates the ratings — if that happens,
wipe and reload (step 3 again). To go back to the sample later, set
`AUTO_SEED: "true"` again and do `docker compose down -v` followed by
`docker compose up -d`.

## Tools used

- pandas, to read the large CSVs efficiently in the loader.
- SQLAlchemy's `bulk_save_objects`, for fast batched inserts.
- Python's built-in `csv` module for the small sample seeder.
