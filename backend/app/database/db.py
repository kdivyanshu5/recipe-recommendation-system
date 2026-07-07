"""Database engine, session factory and the FastAPI session dependency."""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# pool_pre_ping avoids "server closed the connection" errors after the
# database container restarts.
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class every ORM model inherits from.
Base = declarative_base()


def get_db():
    """Yield a database session and always close it afterwards.

    Used as a FastAPI dependency so each request gets its own session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
