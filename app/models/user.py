from sqlalchemy import Column, Integer, String
from app.db.base import Base
from sqlalchemy.orm import relationship



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="consumer")

    products = relationship("Product", back_populates="supplier", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="consumer", cascade="all, delete-orphan")
