from pydantic import BaseModel, EmailStr
from typing import Literal

class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

class UserCreate(UserBase):
    password: str
    role: Literal["consumer", "supplier"] = "consumer"

class UserRead(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True