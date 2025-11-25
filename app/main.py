from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db  # Importing to ensure DB session setup


app = FastAPI()


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "ok"}
