from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# The database URL for SQLite. Creates `leads.db` for running locally
SQLALCHEMY_DATABASE_URL = "sqlite:///./leads.db"

# Create the SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Create new DB session per request and close it after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()