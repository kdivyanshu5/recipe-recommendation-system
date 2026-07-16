# How to Use

Once the app is running (see **How to install.md**), open
<http://localhost:8080>. This guide covers using the web app and calling the API
directly.

---

## Using the web app

### 1. Landing page

When the page loads it shows a **"Popular right now"** list so you always have
something to look at. Each card shows the recipe name, cooking time, ingredient
count, average star rating, and tags.

### 2. Enter your preferences

Fill in the form at the top:

- **Ingredients you have** — type a comma-separated list, e.g.
  `chicken, garlic, rice`. The recommender favours recipes that use them.
- **Craving…** — tap the mood chips (`vegetarian`, `quick`, `dinner`,
  `dessert`, `spicy`, …). Tap again to unselect. You can pick several.
- **Avoid these** — ingredients that must **not** appear, e.g. `peanuts`.
- **Max minutes** — only show recipes that cook within this time.
- **Min rating** — only show recipes at or above this average rating (0–5).

### 3. Get matches

Press **Find recipes**. Results are ranked by relevance and each card shows:

- a **match percentage** (how well it fits your request),
- **star rating** and number of ratings,
- **tags**, and
- **reasons** it was chosen, e.g. *"Uses chicken, garlic"*,
  *"Matches dinner"*, *"Highly rated (4.5 stars)"*, *"Quick to make"*.

### 4. Explore similar recipes

Click **"More like this →"** on any card to see recipes that share ingredients
and style with it. The heading updates to *More like "…"* and the page scrolls
back to the top.

### Tips

- Start broad (a couple of ingredients or one chip) and add filters to narrow
  down.
- If you get *"No matches"*, loosen a filter — lower the min rating, raise the
  max minutes, or remove an excluded ingredient.
- Preferences are optional. With none set, results fall back to the most popular
  recipes.

---

## Using the API directly

The backend is a normal REST API. Explore it interactively at
<http://localhost:8000/docs>.

Base URL: `http://localhost:8000` (or `/api` through the frontend proxy).

> **Windows note:** run these in the VS Code terminal. The `curl` examples below
> are for Mac/Linux — in Windows PowerShell, `curl` is an alias for a different
> command, so use `Invoke-RestMethod` instead (PowerShell versions shown after
> each example), or just use the Swagger page at
> <http://localhost:8000/docs>, which needs no commands at all.

### Recommend by preferences (main endpoint)

```bash
curl -X POST http://localhost:8000/recommend/ \
  -H "Content-Type: application/json" \
  -d '{
        "ingredients": ["chicken", "garlic"],
        "tags": ["dinner"],
        "exclude_ingredients": ["peanuts"],
        "max_minutes": 60,
        "min_rating": 3.5,
        "limit": 5
      }'
```

Windows (PowerShell):

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/recommend/ -ContentType "application/json" -Body '{"ingredients":["chicken","garlic"],"tags":["dinner"],"exclude_ingredients":["peanuts"],"max_minutes":60,"min_rating":3.5,"limit":5}'
```

Response (shortened):

```json
{
  "count": 5,
  "results": [
    {
      "recipe": { "id": 100003, "name": "chicken tikka masala", "minutes": 55,
                  "tags": ["indian", "dinner"], "ingredients": ["chicken", "..."] },
      "score": 0.41,
      "avg_rating": 4.5,
      "num_ratings": 6,
      "reasons": ["Uses chicken", "Matches dinner", "Highly rated (4.5 stars)"]
    }
  ]
}
```

### Other useful endpoints

| Method | Endpoint                    | What it does                          |
|--------|-----------------------------|---------------------------------------|
| GET    | `/health`                   | Service + DB status, recipe count     |
| GET    | `/recipes/?skip=0&limit=20` | Browse recipes (paginated)            |
| GET    | `/recipes/search?q=chicken` | Search recipes by name                |
| GET    | `/recipes/{id}`             | Full detail for one recipe            |
| GET    | `/recommend/popular`        | Most popular recipes                  |
| GET    | `/recommend/similar/{id}`   | "More like this" for a recipe         |
| POST   | `/recommend/quantum`        | Optional QAOA diversity demo          |
| POST   | `/admin/rebuild`            | Rebuild the engine after loading data |

Examples:

```bash
# Popular recipes
curl http://localhost:8000/recommend/popular?limit=8

# Recipes similar to recipe 100000
curl http://localhost:8000/recommend/similar/100000?limit=6

# Search by name
curl "http://localhost:8000/recipes/search?q=soup"
```

Windows (PowerShell):

```powershell
Invoke-RestMethod http://localhost:8000/recommend/popular?limit=8
Invoke-RestMethod http://localhost:8000/recommend/similar/100000?limit=6
Invoke-RestMethod "http://localhost:8000/recipes/search?q=soup"
```

---

## How the recommendations are made

Behind the scenes the engine blends three signals:

1. **Content match** — each recipe becomes a short "document" of its ingredients
   and tags; your preferences are compared to every recipe using TF-IDF cosine
   similarity.
2. **Graph** — recipes are linked when they share ingredients (NetworkX), which
   powers "More like this".
3. **Popularity** — average user rating nudges the ranking toward recipes people
   actually liked.

The final preference score is `0.75 × content + 0.25 × rating`, after applying
your hard filters (max time, min rating, excluded ingredients). See
`docs/architecture.md` for the full picture.
