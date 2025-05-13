from fastapi import APIRouter, HTTPException
from databases import Database
from typing import List
from models.product import Product

router = APIRouter(prefix="/products", tags=["Products"])
database = Database("sqlite:///C:/Users/THUAN/Desktop/tech/database/ecommerce.db")

@router.get("/search", response_model=List[Product])
async def search_products(
    q: str = None,  # Từ khóa tìm kiếm
    category_id: int = None,  # Bộ lọc danh mục
    min_price: float = None,  # Bộ lọc giá tối thiểu
    max_price: float = None,  # Bộ lọc giá tối đa
    color: str = None  # Bộ lọc màu sắc
):
    # Truy vấn chính từ products và product_variants
    query = """
        SELECT p.product_id, p.name, p.description, p.base_price, p.category_id, p.created_at
        FROM products p
        LEFT JOIN product_variants pv ON p.product_id = pv.product_id
    """
    params = {}

    conditions = []
    if q:
        try:
            fts_query = """
                SELECT product_id FROM products_fts WHERE products_fts MATCH :q
            """
            fts_results = await database.fetch_all(fts_query, {"q": q})
            if fts_results:
                product_ids = [row["product_id"] for row in fts_results]
                conditions.append(f"p.product_id IN ({','.join(map(str, product_ids))})")
            else:
                conditions.append("(p.name LIKE :q OR p.description LIKE :q)")
                params["q"] = f"%{q}%"
        except Exception as e:
            conditions.append("(p.name LIKE :q OR p.description LIKE :q)")
            params["q"] = f"%{q}%"

    if category_id:
        conditions.append("p.category_id = :category_id")
        params["category_id"] = category_id
    if min_price is not None:
        conditions.append("p.base_price >= :min_price")
        params["min_price"] = min_price
    if max_price is not None:
        conditions.append("p.base_price <= :max_price")
        params["max_price"] = max_price
    if color:
        conditions.append("pv.color = :color COLLATE NOCASE")
        params["color"] = color

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " GROUP BY p.product_id"

    products = await database.fetch_all(query, params)
    if not products:
        return []

    result = []
    for product in products:
        # Lấy biến thể với điều kiện color nếu có
        query_variants = """
            SELECT variant_id, product_id, color, size, sku
            FROM product_variants
            WHERE product_id = :product_id
        """
        variant_params = {"product_id": product["product_id"]}
        if color:  # Nếu có tham số color, thêm điều kiện lọc
            query_variants += " AND color = :color COLLATE NOCASE"
            variant_params["color"] = color

        variants = await database.fetch_all(query_variants, variant_params)
        product_dict = dict(product)
        product_dict["variants"] = [dict(variant) for variant in variants]
        result.append(product_dict)

    return result