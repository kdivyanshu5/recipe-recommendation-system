# Database schema

PostgreSQL 16. Two tables, mirroring the Food.com dataset layout.

## `recipes`

| Column          | Type     | Notes                                             |
|-----------------|----------|---------------------------------------------------|
| id              | integer  | Primary key (recipe id from the dataset)          |
| name            | text     | Recipe name, indexed                              |
| minutes         | integer  | Total time to make                                |
| contributor_id  | integer  | Author id from the dataset                        |
| submitted       | date     | Date the recipe was submitted                     |
| tags            | text     | Stringified list, e.g. `['italian','vegetarian']` |
| nutrition       | text     | Stringified list of nutrition values              |
| n_steps         | integer  | Number of steps                                   |
| steps           | text     | Stringified list of step strings                  |
| description     | text     | Free-text description                             |
| ingredients     | text     | Stringified list of ingredients                   |
| n_ingredients   | integer  | Number of ingredients                             |

List-like columns are stored exactly as the dataset provides them (a string that
looks like a Python list). The backend parses them into real lists in the schema
layer (`app/utils/parsing.py`), which keeps the sample data and the full dataset
byte-compatible.

## `interactions`

| Column     | Type     | Notes                                    |
|------------|----------|------------------------------------------|
| id         | integer  | Primary key, auto-increment              |
| user_id    | integer  | Reviewer id, indexed                     |
| recipe_id  | integer  | Recipe reviewed, indexed                 |
| date       | date     | Date of the interaction                  |
| rating     | integer  | 0–5 star rating                          |
| review     | text     | Free-text review                         |

## How it is populated

- **Automatically:** on first startup the backend seeds the sample CSVs from
  `data/` if the tables are empty (`app/utils/seed.py`).
- **Manually (full data):** `backend/scripts/load_full_dataset.py` bulk-loads
  the real RAW CSVs (see `docs/data_preparation.md`).

Ratings are aggregated per recipe with a single grouped query
(`InteractionRepository.rating_stats`) and fed into the recommender as a
quality/popularity signal.
