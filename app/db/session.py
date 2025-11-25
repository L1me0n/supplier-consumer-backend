from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL

# The main connection to the database
engine = create_engine(DATABASE_URL, echo=True)

# Factory to create DB sessions (objects to talk to the DB)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# This will be used in FastAPI endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
