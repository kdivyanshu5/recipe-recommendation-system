"""Optional quantum re-ranking demo (disabled by default).

This module showcases how a quantum optimiser could pick a *diverse* short-list
of recipes from a larger candidate set. It frames the choice as a small QUBO /
Max-Cut-style problem: reward recipes with a high base score, penalise pairs
that are too similar, and let QAOA search for a good subset.

It is intentionally isolated from the rest of the app:

* Qiskit is **not** a core dependency and is never imported at module load time.
* The core recommender works fully without it.
* It is only reachable when ``ENABLE_QUANTUM=true`` *and* the extra packages in
  ``requirements-quantum.txt`` are installed.

If either condition is missing, :func:`quantum_rerank` raises
``QuantumUnavailable`` and the API returns a friendly 503 with instructions.
"""

from typing import List

from app.config import settings


class QuantumUnavailable(RuntimeError):
    """Raised when the quantum demo is disabled or Qiskit is not installed."""


def is_available() -> bool:
    """True only when the feature is enabled and Qiskit can be imported."""
    if not settings.ENABLE_QUANTUM:
        return False
    try:
        import qiskit  # noqa: F401
        import qiskit_optimization  # noqa: F401
    except ImportError:
        return False
    return True


def quantum_rerank(candidates: List[dict], k: int, similarity) -> List[dict]:
    """Pick ``k`` recipes that are both high-scoring and diverse using QAOA.

    ``candidates`` is a list of dicts with at least ``index`` and ``score``.
    ``similarity`` is a callable ``similarity(i, j) -> float`` giving how alike two
    candidate rows are (0-1). Returns the chosen candidate dicts.

    Raises :class:`QuantumUnavailable` if the optional stack is not present.
    """
    if not settings.ENABLE_QUANTUM:
        raise QuantumUnavailable(
            "Quantum demo is disabled. Set ENABLE_QUANTUM=true to turn it on."
        )

    try:
        from qiskit_optimization import QuadraticProgram
        from qiskit_optimization.algorithms import MinimumEigenOptimizer
        from qiskit_algorithms import QAOA
        from qiskit_algorithms.optimizers import COBYLA
        from qiskit.primitives import Sampler
    except ImportError as exc:  # pragma: no cover - depends on optional extras
        raise QuantumUnavailable(
            "Qiskit is not installed. Install it with: "
            "pip install -r backend/requirements-quantum.txt"
        ) from exc

    n = len(candidates)
    if n == 0:
        return []
    k = max(1, min(k, n))

    # Build a QUBO: maximise total score, minimise pairwise similarity, and
    # softly enforce that exactly k recipes are chosen.
    problem = QuadraticProgram("diverse_recipes")
    for i in range(n):
        problem.binary_var(name=f"x{i}")

    linear = {f"x{i}": float(candidates[i]["score"]) for i in range(n)}
    quadratic = {}
    diversity_weight = 1.5
    for i in range(n):
        for j in range(i + 1, n):
            quadratic[(f"x{i}", f"x{j}")] = -diversity_weight * float(similarity(i, j))

    # We maximise reward, so express it as a maximisation objective.
    problem.maximize(linear=linear, quadratic=quadratic)
    problem.linear_constraint(
        linear={f"x{i}": 1 for i in range(n)}, sense="==", rhs=k, name="pick_k"
    )

    optimizer = MinimumEigenOptimizer(QAOA(sampler=Sampler(), optimizer=COBYLA(), reps=1))
    result = optimizer.solve(problem)

    chosen = [i for i in range(n) if result.x[i] > 0.5]
    if not chosen:  # Fallback to plain top-k if the solver returned nothing.
        chosen = sorted(range(n), key=lambda i: candidates[i]["score"], reverse=True)[:k]
    return [candidates[i] for i in chosen]
