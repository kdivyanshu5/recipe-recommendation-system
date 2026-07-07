# Sample data

These CSVs are a small, self-contained sample used to seed the database on first
startup so the app is plug-and-play. They keep the exact column layout of the
Food.com dataset.

- `recipes_sample.csv` — 50 recipes (mirrors `RAW_recipes.csv`).
- `interactions_sample.csv` — synthetic user ratings (mirrors `RAW_interactions.csv`).

Regenerate them with:

```bash
python backend/scripts/generate_sample_data.py
```

For the full dataset, see [`../docs/data_preparation.md`](../docs/data_preparation.md).

**Source of the real data:** Food.com Recipes and User Interactions —
<https://www.kaggle.com/datasets/shuyangli94/food-com-recipes-and-user-interactions>
