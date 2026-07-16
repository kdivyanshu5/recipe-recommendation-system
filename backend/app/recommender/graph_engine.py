"""Ingredient-graph analysis with NetworkX.

Recipes are nodes. Two recipes are connected by an edge when they share
ingredients, and the edge weight is the number of shared ingredients. This lets
us answer "which recipes are neighbours of this one?" in graph terms, which is a
nice complement to the TF-IDF similarity.
"""

from itertools import combinations
from typing import Dict, List

import networkx as nx

from app.utils.parsing import parse_list


class IngredientGraph:
    """A weighted recipe graph built from shared ingredients."""

    def __init__(self, recipes: List, min_shared: int = 2):
        self.graph = nx.Graph()
        self.min_shared = min_shared
        self._build(recipes)

    def _build(self, recipes: List) -> None:
        # Map every ingredient to the set of recipes that use it. This avoids an
        # expensive all-pairs comparison across the whole collection.
        ingredient_to_recipes: Dict[str, List[int]] = {}

        for recipe in recipes:
            self.graph.add_node(recipe.id, name=recipe.name)
            for ingredient in parse_list(recipe.ingredients):
                key = ingredient.lower().strip()
                ingredient_to_recipes.setdefault(key, []).append(recipe.id)

        # Skip ingredients used by a huge number of recipes (salt, water,
        # onion...). They carry no similarity signal, and pairing up every
        # recipe that shares them makes the edge count explode on big datasets.
        max_uses = 50

        # Count how many ingredients each pair of recipes has in common.
        shared_counts: Dict[tuple, int] = {}
        for recipe_ids in ingredient_to_recipes.values():
            unique_ids = sorted(set(recipe_ids))
            if len(unique_ids) > max_uses:
                continue
            for first, second in combinations(unique_ids, 2):
                shared_counts[(first, second)] = shared_counts.get((first, second), 0) + 1

        for (first, second), count in shared_counts.items():
            if count >= self.min_shared:
                self.graph.add_edge(first, second, weight=count)

    def neighbours(self, recipe_id: int, limit: int = 10) -> List[tuple]:
        """Return ``[(recipe_id, shared_ingredient_count), ...]`` best first."""
        if recipe_id not in self.graph:
            return []
        scored = [
            (other, self.graph[recipe_id][other]["weight"])
            for other in self.graph.neighbors(recipe_id)
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:limit]

    def degree_centrality(self) -> Dict[int, float]:
        """How connected each recipe is - a simple 'versatility' signal."""
        if self.graph.number_of_nodes() == 0:
            return {}
        return nx.degree_centrality(self.graph)
