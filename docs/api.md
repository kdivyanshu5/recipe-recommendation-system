# API reference

Base URL (through the frontend proxy): `/api`
Base URL (direct to backend): `http://localhost:8000`

Interactive docs are always available at `http://localhost:8000/docs`.

---

## Health

### `GET /health`
Returns service status, the number of recipes loaded, and whether the quantum
demo is enabled/available.

```json
{ "status": "ok", "recipes": 50, "quantum_enabled": false, "quantum_available": false }
```

---

## Recipes

### `GET /recipes/?skip=0&limit=20`
A page of recipes (summary view).

### `GET /recipes/search?q=chicken&limit=20`
Search recipes by name (case-insensitive substring match).

### `GET /recipes/{id}`
Full detail for one recipe, including parsed `steps`, `nutrition`, `ingredients`
and `tags`. Returns `404` if the recipe does not exist.

---

## Recommendations

### `POST /recommend/`
The main matching endpoint. Body:

```json
{
  "ingredients": ["chicken", "garlic"],
  "tags": ["dinner"],
  "exclude_ingredients": ["peanuts"],
  "max_minutes": 60,
  "min_rating": 3.5,
  "limit": 10
}
```

All fields are optional except that at least ingredients or tags are needed for
a meaningful content match (otherwise results fall back to popularity). Response:

```json
{
  "count": 2,
  "results": [
    {
      "recipe": { "id": 100003, "name": "chicken tikka masala", "minutes": 55,
                  "n_ingredients": 8, "tags": ["indian","dinner"], "ingredients": ["chicken","..."] },
      "score": 0.41,
      "avg_rating": 4.5,
      "num_ratings": 6,
      "reasons": ["Uses chicken", "Matches dinner", "Highly rated (4.5 stars)"]
    }
  ]
}
```

`score` is a 0–1 blended relevance score. `reasons` are human-readable
explanations for the match.

### `GET /recommend/popular?limit=10`
Highest-rated, most-rated recipes. Used as the default view on page load.

### `GET /recommend/similar/{recipe_id}?limit=10`
"More like this": recipes similar to the given one, blending content similarity
with the ingredient graph. Returns `404` if the recipe is unknown.

### `POST /recommend/quantum`
Optional QAOA diversity demo. Same request body as `/recommend/`. Returns `503`
with instructions when `ENABLE_QUANTUM` is false or Qiskit is not installed.

---

## Admin

### `POST /admin/rebuild`
Drops the cached recommendation engine and rebuilds it from the current database.
Call this after importing the full dataset so the new data is used without
restarting the container.
