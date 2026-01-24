from pydantic import BaseModel

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

class OrderItemRead(OrderItemCreate):
    unit_price: float

    class Config:
        orm_mode = True

class OrderRead(BaseModel):
    id: int
    consumer_id: int
    status: str
    items: list[OrderItemRead]

    class Config:
        orm_mode = True