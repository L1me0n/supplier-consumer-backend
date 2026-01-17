from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float

class ProductRead(ProductCreate):
    id: int
    supplier_id: int

    class Config:
        orm_mode = True