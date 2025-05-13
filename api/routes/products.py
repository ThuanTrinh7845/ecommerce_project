from fastapi import APIRouter, HTTPException
from databases import Database
from typing import List
from models.product import Product

router = APIRouter(prefix="/categories", tags=["Products"])
database = Database("sqlite:///C:/Users/THUAN/Desktop/tech/database/ecommerce.db")

@router.get("/{category_id}/products", response_model=List[Product])
async def get_products_by_category(category_id: int):
    # kiểm tra category có tồn tại không
    query_check_category = "SELECT 1 FROM categories WHERE category_id = :category_id"
    category_exist = await database.fetch_one(query_check_category, {"category_id": category_id})
    if not category_exist:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # lấy danh sách sản phẩm trong danh mục
    query_products = """
        SELECT product_id, name, description, base_price, category_id, created_at
        FROM products
        WHERE category_id = :category_id
    """

    products = await database.fetch_all(query_products, {"category_id": category_id})
    
    if not products:
        return []

    # lấy variants cho từng product
    result = []
    for product in products:
        query_variants = """
            SELECT variant_id, product_id, color, size, sku
            FROM product_variants
            WHERE product_id = :product_id
        """
        variants = await database.fetch_all(query_variants, {"product_id": product["product_id"]})
        product_dict = dict(product)
        product_dict["variants"] = [dict(variant) for variant in variants]
        result.append(product_dict)
    
    return result