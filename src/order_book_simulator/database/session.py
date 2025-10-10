from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from contextlib import contextmanager
from pathlib import Path

from .models import Base

# Create database directory if it doesn't exist
DB_DIR = Path(__file__).parent.parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)

# SQLite database URL
SQLITE_URL = f"sqlite:///{DB_DIR}/orderbook.db"

# Create engine
# Automatically creates the database file if it doesn't exist
engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},  # Needed for multi-threaded applications
)

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_db() -> Session:
    """Get database session.

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
