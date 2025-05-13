from fastapi import APIRouter
from databases import Database
from typing import List
from models.category import Category

router = APIRouter(prefix="/categories", tags=["Categories"])
database = Database("sqlite:///C:/Users/THUAN/Desktop/tech/database/ecommerce.db")

@router.get("/", response_model=List[Category])
async def get_categories():
    query = "SELECT category_id, name, parent_id, discount_percentage FROM categories"
    results = await database.fetch_all(query)
    return [dict(row) for row in results]