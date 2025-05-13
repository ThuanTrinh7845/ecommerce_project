from pydantic import BaseModel
from typing import List

class OrderItemCreate(BaseModel):
    variant_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    address_id: int
    payment_method: str
    items: List[OrderItemCreate]

class OrderItem(BaseModel):
    order_item_id: int
    order_id: int
    variant_id: int
    quantity: int
    unit_price: float
    discount: float

class Order(BaseModel):
    order_id: int
    user_id: int
    address_id: int
    order_date: str
    status: str
    subtotal: float
    shipping_fee: float
    tax: float
    total: float
    payment_method: str
    payment_status: str
    items: List[OrderItem]