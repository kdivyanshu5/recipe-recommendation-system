import RecipeCard from "./RecipeCard.jsx";

// Renders the grid of recommended recipes, or a gentle empty state.
export default function ResultsList({ items, onSimilar }) {
  if (!items || items.length === 0) {
    return <p className="muted">Nothing to show yet. Adjust your preferences and search.</p>;
  }

  return (
    <div className="grid">
      {items.map((item) => (
        <RecipeCard key={item.recipe.id} item={item} onSimilar={onSimilar} />
      ))}
    </div>
  );
}
