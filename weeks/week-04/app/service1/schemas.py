from pydantic import BaseModel
from typing import List, Optional

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: int
    quantity: int

class ProductCreate(BaseModel):
    name: str
    description: str
    price: int
    quantity: int

class CartItem(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    id: str
    items: List[dict]
    total_amount: int
    status: str