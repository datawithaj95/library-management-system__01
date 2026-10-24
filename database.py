from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# PostgreSQL database connection
DATABASE_URL = "postgresql+psycopg://postgres:MyNewPass2026!@localhost:5432/library_db"
engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()