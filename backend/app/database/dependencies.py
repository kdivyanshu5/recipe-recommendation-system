"""Backward-compatible re-export of the database session dependency."""

from app.database.db import get_db

__all__ = ["get_db"]
