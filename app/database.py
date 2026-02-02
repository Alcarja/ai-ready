from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator

# Database URL - SQLite file in the project root
DATABASE_URL = "sqlite:///./database.db"

# Create the SQLAlchemy engine
# connect_args={"check_same_thread": False} is needed for SQLite (allows async operations)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Create a session factory
# This is used to create new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all models inherit from
# This allows SQLAlchemy to track and manage your model classes
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI routes.
    Provides a database session to routes that need it.

    Usage in routes:
    @router.get("/items/")
    def get_items(db: Session = Depends(get_db)):
        # db is now available in your route
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables defined in models.
    Only creates tables that don't already exist.

    Call this once when your application starts.
    """
    Base.metadata.create_all(bind=engine)
