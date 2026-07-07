import { useEffect, useState } from "react";
import PreferenceForm from "./components/PreferenceForm.jsx";
import ResultsList from "./components/ResultsList.jsx";
import { getPopular, getRecommendations, getSimilar } from "./api.js";

export default function App() {
  const [results, setResults] = useState([]);
  const [heading, setHeading] = useState("Popular right now");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Load a popular list on first render so the page is never empty.
  useEffect(() => {
    let active = true;
    setLoading(true);
    getPopular(8)
      .then((data) => {
        if (active) setResults(data.results);
      })
      .catch((err) => active && setError(err.message))
      .finally(() => active && setLoading(false));
    return () => {
      active = false;
    };
  }, []);

  async function handleSearch(preferences) {
    setLoading(true);
    setError("");
    try {
      const data = await getRecommendations(preferences);
      setResults(data.results);
      setHeading(
        data.count > 0
          ? `Top ${data.count} matches for you`
          : "No matches — try loosening your filters"
      );
    } catch (err) {
      setError(err.message);
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleSimilar(recipeId, name) {
    setLoading(true);
    setError("");
    try {
      const data = await getSimilar(recipeId, 6);
      setResults(data.results);
      setHeading(`More like "${name}"`);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <header className="hero">
        <div className="hero-inner">
          <span className="logo-dot" />
          <h1>FlavorGraph</h1>
          <p>Tell us what you have and how you feel like eating. We'll match recipes for you.</p>
        </div>
      </header>

      <main className="container">
        <PreferenceForm onSearch={handleSearch} loading={loading} />

        {error && <p className="error">⚠ {error}</p>}

        <section className="results">
          <h2>{heading}</h2>
          {loading ? (
            <p className="muted">Finding recipes…</p>
          ) : (
            <ResultsList items={results} onSimilar={handleSimilar} />
          )}
        </section>
      </main>

      <footer className="footer">
        <p>
          Data: Food.com Recipes &amp; User Interactions. Content-based + graph +
          rating recommender.
        </p>
      </footer>
    </div>
  );
}
