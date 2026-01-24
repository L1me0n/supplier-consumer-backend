from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float

class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None

class ProductRead(ProductCreate):
    id: int
    supplier_id: int

    class Config:
        orm_mode = True