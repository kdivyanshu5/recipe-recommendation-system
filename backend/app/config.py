"""Application configuration.

All settings are read from environment variables so the same image works in
Docker and on a local machine. Sensible defaults are provided so the project
runs with zero configuration.
"""

import os


def _as_bool(value: str) -> bool:
    """Turn a string environment value into a boolean."""
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    """Central place for every tunable value in the backend."""

    APP_NAME = "FlavorGraph Recipe Recommendation API"
    VERSION = "1.0.0"

    # --- Database connection -------------------------------------------------
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "recipe_db")

    # --- Seeding -------------------------------------------------------------
    # When true, the sample CSVs are loaded on startup if the tables are empty.
    AUTO_SEED = _as_bool(os.getenv("AUTO_SEED", "true"))
    SEED_RECIPES_PATH = os.getenv("SEED_RECIPES_PATH", "/data/recipes_sample.csv")
    SEED_INTERACTIONS_PATH = os.getenv(
        "SEED_INTERACTIONS_PATH", "/data/interactions_sample.csv"
    )

    # --- Optional quantum demo module ---------------------------------------
    # Disabled by default. Requires the extra dependencies in
    # requirements-quantum.txt. The core app never imports Qiskit.
    ENABLE_QUANTUM = _as_bool(os.getenv("ENABLE_QUANTUM", "false"))

    # --- API -----------------------------------------------------------------
    # Comma separated list of allowed CORS origins, or "*" for any.
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    @property
    def database_url(self) -> str:
        """Full SQLAlchemy connection string for PostgreSQL."""
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def cors_origins_list(self) -> list:
        """CORS origins parsed into a list for FastAPI middleware."""
        if self.CORS_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
