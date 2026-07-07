import { useState } from "react";

// A curated set of tag chips users can toggle. Kept short and friendly.
const TAG_OPTIONS = [
  "vegetarian",
  "vegan",
  "quick",
  "dinner",
  "breakfast",
  "dessert",
  "spicy",
  "healthy",
  "soup",
  "curry",
];

// Turn a comma/space separated string into a clean list of tokens.
function toList(text) {
  return text
    .split(",")
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean);
}

export default function PreferenceForm({ onSearch, loading }) {
  const [ingredients, setIngredients] = useState("");
  const [exclude, setExclude] = useState("");
  const [selectedTags, setSelectedTags] = useState([]);
  const [maxMinutes, setMaxMinutes] = useState("");
  const [minRating, setMinRating] = useState("");

  function toggleTag(tag) {
    setSelectedTags((current) =>
      current.includes(tag)
        ? current.filter((item) => item !== tag)
        : [...current, tag]
    );
  }

  function submit(event) {
    event.preventDefault();
    onSearch({
      ingredients: toList(ingredients),
      exclude_ingredients: toList(exclude),
      tags: selectedTags,
      max_minutes: maxMinutes ? Number(maxMinutes) : null,
      min_rating: minRating ? Number(minRating) : null,
      limit: 12,
    });
  }

  return (
    <form className="card form" onSubmit={submit}>
      <div className="field">
        <label htmlFor="ingredients">Ingredients you have</label>
        <input
          id="ingredients"
          type="text"
          placeholder="e.g. chicken, garlic, rice"
          value={ingredients}
          onChange={(event) => setIngredients(event.target.value)}
        />
      </div>

      <div className="field">
        <label>Craving…</label>
        <div className="chips">
          {TAG_OPTIONS.map((tag) => (
            <button
              type="button"
              key={tag}
              className={`chip ${selectedTags.includes(tag) ? "chip-on" : ""}`}
              onClick={() => toggleTag(tag)}
            >
              {tag}
            </button>
          ))}
        </div>
      </div>

      <div className="row">
        <div className="field">
          <label htmlFor="exclude">Avoid these</label>
          <input
            id="exclude"
            type="text"
            placeholder="e.g. peanuts"
            value={exclude}
            onChange={(event) => setExclude(event.target.value)}
          />
        </div>
        <div className="field small">
          <label htmlFor="minutes">Max minutes</label>
          <input
            id="minutes"
            type="number"
            min="1"
            placeholder="any"
            value={maxMinutes}
            onChange={(event) => setMaxMinutes(event.target.value)}
          />
        </div>
        <div className="field small">
          <label htmlFor="rating">Min rating</label>
          <input
            id="rating"
            type="number"
            min="0"
            max="5"
            step="0.5"
            placeholder="any"
            value={minRating}
            onChange={(event) => setMinRating(event.target.value)}
          />
        </div>
      </div>

      <button className="submit" type="submit" disabled={loading}>
        {loading ? "Matching…" : "Find recipes"}
      </button>
    </form>
  );
}
