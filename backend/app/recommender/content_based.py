"""Content-based similarity using TF-IDF over ingredients and tags.

Each recipe is turned into a short "document" made of its ingredients and tags.
A TF-IDF vector space is fitted over all recipes once, then:

* a user's preferences are vectorized into the same space and compared to every
  recipe (preference matching), and
* any two recipes can be compared directly ("more like this").

This is a classic, transparent content-based recommender - no training data or
GPU required, so it runs anywhere.
"""

from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.parsing import parse_list


def _recipe_to_document(recipe) -> str:
    """Build the text used to represent a recipe in the vector space.

    Ingredients are repeated once and tags once; spaces inside a token are
    replaced with underscores so "olive oil" stays a single feature.
    """
    tokens = []
    for item in parse_list(recipe.ingredients) + parse_list(recipe.tags):
        cleaned = item.lower().strip().replace(" ", "_")
        if cleaned:
            tokens.append(cleaned)
    return " ".join(tokens)


class ContentModel:
    """Fitted TF-IDF model over the recipe collection."""

    def __init__(self, recipes: List):
        self.recipes = recipes
        self.documents = [_recipe_to_document(recipe) for recipe in recipes]
        self.vectorizer = TfidfVectorizer(token_pattern=r"[^\s]+")
        # matrix shape: (num_recipes, num_features)
        self.matrix = self.vectorizer.fit_transform(self.documents)

    def score_preferences(self, ingredients: List[str], tags: List[str]):
        """Return a cosine-similarity score for every recipe against a query.

        The query is built from the requested ingredients and tags exactly the
        same way recipes are, so identical terms line up in the vector space.
        """
        query_tokens = []
        for item in list(ingredients) + list(tags):
            cleaned = str(item).lower().strip().replace(" ", "_")
            if cleaned:
                query_tokens.append(cleaned)

        if not query_tokens:
            # No preferences given -> neutral score for everything.
            return [0.0] * len(self.recipes)

        query_vector = self.vectorizer.transform([" ".join(query_tokens)])
        scores = cosine_similarity(query_vector, self.matrix)[0]
        return scores.tolist()

    def similar_to_index(self, index: int):
        """Cosine similarity of one recipe (by row index) to all others."""
        scores = cosine_similarity(self.matrix[index], self.matrix)[0]
        return scores.tolist()
