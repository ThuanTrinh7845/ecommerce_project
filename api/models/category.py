from pydantic import BaseModel
from typing import Optional

class Category(BaseModel):
    category_id: int
    name: str
    parent_id: Optional[int] = None
    discount_percentage: float
