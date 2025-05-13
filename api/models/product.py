from pydantic import BaseModel
from typing import List, Optional

class ProductVariant(BaseModel):
    variant_id: int
    product_id: int
    color: str
    size: str
    sku: Optional[str] = None

class Product(BaseModel):
    product_id: int
    name: str
    description: Optional[str] = None
    base_price: float
    category_id: int
    created_at: str
    variants: List[ProductVariant] = []