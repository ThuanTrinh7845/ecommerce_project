from fastapi import APIRouter, HTTPException, BackgroundTasks
from databases import Database
from typing import List
from datetime import datetime
from models.order import OrderCreate, Order, OrderItem
from fastapi_mail import MessageSchema, MessageType
from config.email import fm

router = APIRouter(prefix="/orders", tags=["Orders"])
database = Database("sqlite:///C:/Users/THUAN/Desktop/tech/database/ecommerce.db")

async def send_order_confirmation_email(order_id: int, user_id: int):
    # Lấy thông tin user (email)
    user_query = "SELECT email FROM users WHERE user_id = :user_id"
    user = await database.fetch_one(user_query, {"user_id": user_id})
    if not user:
        print(f"Không tìm thấy người dùng với user_id {user_id}")
        return

    # Lấy thông tin đơn hàng
    order_query = """
        SELECT order_id, user_id, address_id, order_date, status, subtotal, shipping_fee, tax, total, payment_method, payment_status
        FROM orders
        WHERE order_id = :order_id
    """
    order = await database.fetch_one(order_query, {"order_id": order_id})
    if not order:
        print(f"Không tìm thấy đơn hàng với order_id {order_id}")
        return

    # Lấy chi tiết đơn hàng
    items_query = """
        SELECT oi.order_item_id, oi.order_id, oi.variant_id, oi.quantity, oi.unit_price, oi.discount,
               p.name AS product_name
        FROM order_items oi
        JOIN product_variants pv ON oi.variant_id = pv.variant_id
        JOIN products p ON pv.product_id = p.product_id
        WHERE oi.order_id = :order_id
    """
    items = await database.fetch_all(items_query, {"order_id": order_id})

    # Tạo nội dung email dạng văn bản thô
    email_body = f"Order Confirmation - Order #{order['order_id']}\n\n"
    email_body += "Dear Customer,\n\n"
    email_body += "Thank you for your order! Below are the details of your purchase:\n\n"
    email_body += "Items:\n"
    for item in items:
        item_total = item["quantity"] * item["unit_price"] - item["discount"]
        email_body += f"- {item['product_name']}: {item['quantity']} x {item['unit_price']} VND (Discount: {item['discount']} VND) = {item_total} VND\n"
    email_body += f"\nSubtotal: {order['subtotal']} VND\n"
    email_body += f"Tax: {order['tax']} VND\n"
    email_body += f"Shipping Fee: {order['shipping_fee']} VND\n"
    email_body += f"Total: {order['total']} VND\n"
    email_body += f"Payment Status: {order['payment_status']}\n\n"
    email_body += "We will process your order soon. If you have any questions, please contact us.\n\n"
    email_body += "Best regards,\nE-commerce Team"

    # Gửi email
    message = MessageSchema(
        subject=f"Order Confirmation - Order #{order_id}",
        recipients=[user["email"]],
        body=email_body,
        subtype=MessageType.plain  # Dạng văn bản thô
    )

    try:
        await fm.send_message(message)
        print(f"Email xác nhận đơn hàng #{order_id} đã được gửi đến {user['email']}")
    except Exception as e:
        print(f"Lỗi khi gửi email xác nhận đơn hàng #{order_id}: {str(e)}")

@router.post("", response_model=Order)
async def create_order(order: OrderCreate, background_tasks: BackgroundTasks):
    # Kiểm tra dữ liệu đầu vào
    if not order.items:
        raise HTTPException(status_code=400, detail="Danh sách sản phẩm không được rỗng")

    # Bắt đầu transaction
    async with database.transaction():
        # Tính toán subtotal và discount
        subtotal = 0.0
        total_discount = 0.0
        items_response = []
        for item in order.items:
            if item.quantity <= 0:
                raise HTTPException(status_code=400, detail=f"Số lượng của variant_id {item.variant_id} phải lớn hơn 0")

            # Lấy thông tin biến thể, giá sản phẩm và discount_percentage
            query = """
                SELECT pv.variant_id, p.base_price, c.discount_percentage
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.product_id
                JOIN categories c ON p.category_id = c.category_id
                WHERE pv.variant_id = :variant_id
            """
            result = await database.fetch_one(query, {"variant_id": item.variant_id})
            if not result:
                raise HTTPException(status_code=404, detail=f"Không tìm thấy variant_id {item.variant_id}")

            unit_price = result["base_price"]
            discount_percentage = result["discount_percentage"] or 0.0
            discount = round(unit_price * item.quantity * discount_percentage, 2)
            item_subtotal = round(unit_price * item.quantity - discount, 2)
            subtotal += item_subtotal
            total_discount += discount

            items_response.append({
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "unit_price": unit_price,
                "discount": discount
            })

        # Tính thuế và phí vận chuyển
        tax = round(subtotal * 0.1, 2)  # 10% thuế
        shipping_fee = 50000.0  # Phí vận chuyển cố định
        total = round(subtotal + tax + shipping_fee, 2)

        # Tạo đơn hàng mới
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        insert_order_query = """
            INSERT INTO orders (user_id, address_id, order_date, status, subtotal, shipping_fee, tax, total, payment_method, payment_status)
            VALUES (:user_id, :address_id, :order_date, :status, :subtotal, :shipping_fee, :tax, :total, :payment_method, :payment_status)
        """
        order_values = {
            "user_id": order.user_id,
            "address_id": order.address_id,
            "order_date": order_date,
            "status": "pending",
            "subtotal": subtotal,
            "shipping_fee": shipping_fee,
            "tax": tax,
            "total": total,
            "payment_method": order.payment_method,
            "payment_status": "pending"
        }
        order_id = await database.execute(insert_order_query, order_values)

        # Thêm chi tiết đơn hàng vào order_items
        for item_data in items_response:
            query = """
                SELECT p.base_price, c.discount_percentage
                FROM product_variants pv
                JOIN products p ON pv.product_id = p.product_id
                JOIN categories c ON p.category_id = c.category_id
                WHERE pv.variant_id = :variant_id
            """
            result = await database.fetch_one(query, {"variant_id": item_data["variant_id"]})
            unit_price = result["base_price"]
            discount_percentage = result["discount_percentage"] or 0.0
            discount = round(unit_price * item_data["quantity"] * discount_percentage, 2)

            insert_item_query = """
                INSERT INTO order_items (order_id, variant_id, quantity, unit_price, discount)
                VALUES (:order_id, :variant_id, :quantity, :unit_price, :discount)
            """
            order_item_id = await database.execute(insert_item_query, {
                "order_id": order_id,
                "variant_id": item_data["variant_id"],
                "quantity": item_data["quantity"],
                "unit_price": unit_price,
                "discount": discount
            })

            # Cập nhật items_response với order_item_id
            for item in items_response:
                if item["variant_id"] == item_data["variant_id"]:
                    item["order_item_id"] = order_item_id
                    item["order_id"] = order_id
                    break

        # Giả lập xử lý thanh toán
        payment_status = process_payment(order.payment_method, total)
        new_payment_status = "paid" if payment_status else "failed"
        new_status = "pending" if payment_status else "cancelled"

        # Cập nhật trạng thái đơn hàng
        update_order_query = """
            UPDATE orders
            SET status = :status, payment_status = :payment_status
            WHERE order_id = :order_id
        """
        await database.execute(update_order_query, {
            "status": new_status,
            "payment_status": new_payment_status,
            "order_id": order_id
        })

        # Thêm tác vụ gửi email vào background
        background_tasks.add_task(send_order_confirmation_email, order_id, order.user_id)

        # Trả về thông tin đơn hàng
        order_response = {
            "order_id": order_id,
            "user_id": order.user_id,
            "address_id": order.address_id,
            "order_date": order_date,
            "status": new_status,
            "subtotal": subtotal,
            "shipping_fee": shipping_fee,
            "tax": tax,
            "total": total,
            "payment_method": order.payment_method,
            "payment_status": new_payment_status,
            "items": [
                {
                    "order_item_id": item["order_item_id"],
                    "order_id": item["order_id"],
                    "variant_id": item["variant_id"],
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "discount": item["discount"]
                }
                for item in items_response
            ]
        }
        return order_response

def process_payment(payment_method: str, amount: float) -> bool:
    import random
    success = random.random() < 0.9
    return success