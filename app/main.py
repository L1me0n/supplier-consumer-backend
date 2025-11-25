from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db, engine
from app.db.base import Base
from app.models.user import User
from app.schemas.user import UserCreate, UserRead


app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "ok"}

@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        password_hash=user_in.password  # In a real app, hash the password!
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get("/users", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users
