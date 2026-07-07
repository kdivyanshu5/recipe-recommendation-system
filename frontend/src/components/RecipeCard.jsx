// A single recommended recipe. Shows why it was picked and a "more like this"
// action that fetches similar recipes.

function Stars({ rating }) {
  if (!rating) return <span className="muted">no ratings yet</span>;
  return (
    <span className="stars" title={`${rating} out of 5`}>
      {"*".repeat(Math.round(rating))}
      {".".repeat(5 - Math.round(rating))}
      <span className="rating-num"> {rating.toFixed(1)}</span>
    </span>
  );
}

export default function RecipeCard({ item, onSimilar }) {
  const { recipe, avg_rating, num_ratings, reasons, score } = item;

  return (
    <article className="card recipe">
      <div className="recipe-head">
        <h3>{recipe.name}</h3>
        <span className="match" title="Match score">
          {Math.round(score * 100)}%
        </span>
      </div>

      <div className="meta">
        {recipe.minutes ? <span>⌛ {recipe.minutes} min</span> : null}
        {recipe.n_ingredients ? <span>🧺 {recipe.n_ingredients} ingredients</span> : null}
        <Stars rating={avg_rating} />
        {num_ratings ? <span className="muted">({num_ratings})</span> : null}
      </div>

      {recipe.tags?.length > 0 && (
        <div className="tag-row">
          {recipe.tags.slice(0, 5).map((tag) => (
            <span className="tag" key={tag}>
              {tag}
            </span>
          ))}
        </div>
      )}

      {reasons?.length > 0 && (
        <ul className="reasons">
          {reasons.map((reason) => (
            <li key={reason}>{reason}</li>
          ))}
        </ul>
      )}

      <button className="ghost" onClick={() => onSimilar(recipe.id, recipe.name)}>
        More like this ➡️
      </button>
    </article>
  );
}
