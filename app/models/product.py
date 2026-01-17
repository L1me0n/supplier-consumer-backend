from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    supplier_id = Column(Integer, ForeignKey("users.id"), nullable=False)