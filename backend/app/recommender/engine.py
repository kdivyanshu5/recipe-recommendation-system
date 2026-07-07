"""The recommendation engine that ties the pieces together.

It combines three signals:

1. **Content match** - TF-IDF cosine similarity between the user's preferences
   and each recipe (``content_based``).
2. **Popularity/quality** - the average user rating from the interactions table.
3. **Graph structure** - the NetworkX ingredient graph for "more like this".

The engine is built once from the database and cached in memory (see
``store.py``). Rebuilding is cheap for the sample data and can be triggered again
after loading the full dataset.
"""

from typing import Dict, List, Optional

from app.recommender.content_based import ContentModel
from app.recommender.graph_engine import IngredientGraph
from app.utils.parsing import parse_list


class RecommendationEngine:
    """Holds the fitted models and answers recommendation queries."""

    def __init__(self, recipes: List, rating_stats: Optional[Dict] = None):
        self.recipes = recipes
        self.rating_stats = rating_stats or {}
        # Fast lookup from a recipe id to its row position.
        self.index_by_id = {recipe.id: i for i, recipe in enumerate(recipes)}

        # Precompute lower-cased ingredient/tag sets for fast reason building.
        self._ingredient_sets = [
            {token.lower() for token in parse_list(recipe.ingredients)} for recipe in recipes
        ]
        self._tag_sets = [
            {token.lower() for token in parse_list(recipe.tags)} for recipe in recipes
        ]

        self.content = ContentModel(recipes) if recipes else None
        self.graph = IngredientGraph(recipes) if recipes else None

    # -- helpers -------------------------------------------------------------
    def _avg_rating(self, recipe_id: int) -> float:
        return self.rating_stats.get(recipe_id, (0.0, 0))[0]

    def _num_ratings(self, recipe_id: int) -> int:
        return self.rating_stats.get(recipe_id, (0.0, 0))[1]

    def _passes_filters(self, i: int, prefs) -> bool:
        recipe = self.recipes[i]
        if prefs.max_minutes is not None and recipe.minutes is not None:
            if recipe.minutes > prefs.max_minutes:
                return False
        if prefs.min_rating is not None:
            if self._avg_rating(recipe.id) < prefs.min_rating:
                return False
        if prefs.exclude_ingredients:
            excluded = {item.lower() for item in prefs.exclude_ingredients}
            if self._ingredient_sets[i] & excluded:
                return False
        return True

    def _build_reasons(self, i: int, wanted_ingredients: set, wanted_tags: set) -> List[str]:
        reasons = []
        matched_ingredients = sorted(self._ingredient_sets[i] & wanted_ingredients)
        if matched_ingredients:
            reasons.append("Uses " + ", ".join(matched_ingredients[:4]))
        matched_tags = sorted(self._tag_sets[i] & wanted_tags)
        if matched_tags:
            reasons.append("Matches " + ", ".join(matched_tags[:4]))

        recipe = self.recipes[i]
        avg = self._avg_rating(recipe.id)
        if avg >= 4.0:
            reasons.append(f"Highly rated ({avg:.1f} stars)")
        if recipe.minutes is not None and recipe.minutes <= 20:
            reasons.append("Quick to make")
        return reasons

    # -- public API ----------------------------------------------------------
    def recommend(self, prefs) -> List[dict]:
        """Rank recipes against a set of user preferences."""
        if not self.recipes:
            return []

        wanted_ingredients = {item.lower() for item in prefs.ingredients}
        wanted_tags = {item.lower() for item in prefs.tags}

        content_scores = self.content.score_preferences(prefs.ingredients, prefs.tags)
        has_preferences = bool(prefs.ingredients or prefs.tags)

        scored = []
        for i, recipe in enumerate(self.recipes):
            if not self._passes_filters(i, prefs):
                continue

            rating_norm = self._avg_rating(recipe.id) / 5.0
            if has_preferences:
                # Content match dominates, quality nudges the ranking.
                final = 0.75 * content_scores[i] + 0.25 * rating_norm
            else:
                # No preferences -> fall back to a popularity ranking.
                final = rating_norm

            scored.append({
                "index": i,
                "recipe": recipe,
                "score": round(float(final), 4),
                "avg_rating": round(self._avg_rating(recipe.id), 2),
                "num_ratings": self._num_ratings(recipe.id),
                "reasons": self._build_reasons(i, wanted_ingredients, wanted_tags),
            })

        scored.sort(key=lambda row: (row["score"], row["avg_rating"]), reverse=True)
        return scored[: prefs.limit]

    def similar(self, recipe_id: int, limit: int = 10) -> List[dict]:
        """Return recipes similar to a given one (content + graph blend)."""
        if recipe_id not in self.index_by_id:
            return []

        base_index = self.index_by_id[recipe_id]
        content_scores = self.content.similar_to_index(base_index)

        # Turn graph neighbour weights into a 0-1 signal.
        neighbour_weights = dict(self.graph.neighbours(recipe_id, limit=len(self.recipes)))
        max_weight = max(neighbour_weights.values(), default=1)

        results = []
        for i, recipe in enumerate(self.recipes):
            if i == base_index:
                continue
            graph_score = neighbour_weights.get(recipe.id, 0) / max_weight
            blended = 0.7 * content_scores[i] + 0.3 * graph_score
            if blended <= 0:
                continue
            results.append({
                "index": i,
                "recipe": recipe,
                "score": round(float(blended), 4),
                "avg_rating": round(self._avg_rating(recipe.id), 2),
                "num_ratings": self._num_ratings(recipe.id),
                "reasons": ["Similar ingredients and style"],
            })

        results.sort(key=lambda row: (row["score"], row["avg_rating"]), reverse=True)
        return results[:limit]

    def popular(self, limit: int = 10) -> List[dict]:
        """Highest rated recipes with the most ratings."""
        rows = []
        for i, recipe in enumerate(self.recipes):
            rows.append({
                "index": i,
                "recipe": recipe,
                "score": round(self._avg_rating(recipe.id) / 5.0, 4),
                "avg_rating": round(self._avg_rating(recipe.id), 2),
                "num_ratings": self._num_ratings(recipe.id),
                "reasons": ["Popular with other users"],
            })
        rows.sort(key=lambda row: (row["avg_rating"], row["num_ratings"]), reverse=True)
        return rows[:limit]

    def content_similarity(self, i: int, j: int) -> float:
        """Cosine similarity between two recipe rows (used by the quantum demo)."""
        return float(self.content.similar_to_index(i)[j])
