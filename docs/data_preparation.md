# Data preparation

## Source

Food.com Recipes and User Interactions
<https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions>

Files used:

- `RAW_recipes.csv` — recipe metadata (name, minutes, tags, ingredients, steps…).
- `RAW_interactions.csv` — user ratings and reviews (user_id, recipe_id, rating).

The dataset is credited to the paper *"Generating Personalized Recipes from
Historical User Preferences"* (Majumder et al., EMNLP 2019).

## Why a sample is bundled

`RAW_interactions.csv` alone is ~350 MB (1.1M rows) and the full version 2 is
~900 MB. Importing that on every `docker compose up` would be slow and would
require the grader to download the data first — which breaks "plug and play".

So the repository ships a small, deterministic **sample** with the identical
column layout. The same parsing and loading code path works for both, so nothing
special happens when you later switch to the full data.

## Regenerating the sample

The sample is produced by a self-contained generator (no external data needed):

```bash
python backend/scripts/generate_sample_data.py
# writes data/recipes_sample.csv and data/interactions_sample.csv
```

It builds 50 well-known recipes across cuisines with realistic ingredients,
tags, times and nutrition, plus synthetic user ratings so collaborative/
popularity signals exist. `random.seed(42)` keeps the output stable.

## Loading the full dataset

1. Download `RAW_recipes.csv` and `RAW_interactions.csv` from
   [Kaggle](https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions).
2. Put them in a `data/` folder at the repo root (this folder is gitignored).
3. Rename them with "RAW_recipes.csv -> recipes_sample.csv" and "RAW_interactions.csv -> interactions_sample.csv".
4. Remove container from docker desktop by clicking on delete symbol and re-run :
```bash
docker compose up --build
```

Interactions that reference recipes outside the imported set are
skipped so foreign references stay consistent.

## Tools used

- **pandas** for reading the large CSVs efficiently in the loader.
- **SQLAlchemy** `bulk_save_objects` for fast batched inserts.
- Python's standard `csv` module for the lightweight sample seeder.