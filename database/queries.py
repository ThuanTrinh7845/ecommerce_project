import sqlite3

def insert_assessment_order():
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    
    try:
        # Chèn danh mục
        cursor.execute("INSERT INTO categories (name, discount_percentage) VALUES (?, ?)", ('Sneakers', 0.0))
        category_id = cursor.lastrowid
        
        # Chèn cửa hàng
        cursor.execute("INSERT INTO stores (name, address, contact_phone) VALUES (?, ?, ?)", 
                      ('Main Store', '123 Main Street, Hanoi', '0123456789'))
        store_id = cursor.lastrowid
        
        # Chèn người dùng
        cursor.execute("INSERT INTO users (name, email, phone, password_hash) VALUES (?, ?, ?, ?)", 
                      ('assessment', 'gu@gmail.com', '328355333', 'hashed_password'))
        user_id = cursor.lastrowid
        
        # Chèn địa chỉ
        cursor.execute("INSERT INTO user_addresses (user_id, province, district, commune, address_detail, housing_type, is_default) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                      (user_id, 'Bắc Kạn', 'Ba Bể', 'Phúc Lộc', '73 tân hà 2', 'nhà riêng', 1))
        address_id = cursor.lastrowid
        
        # Chèn sản phẩm
        cursor.execute("INSERT INTO products (name, description, base_price, category_id) VALUES (?, ?, ?, ?)", 
                      ('KAPPA Women''s Sneakers', 'Comfortable women''s sneakers', 980000.00, category_id))
        product_id = cursor.lastrowid
        
        # Chèn biến thể
        cursor.execute("INSERT INTO product_variants (product_id, color, size, sku) VALUES (?, ?, ?, ?)", 
                      (product_id, 'yellow', '36', 'KAPPA_WOMEN_YELLOW_36'))
        variant_id = cursor.lastrowid
        
        # Chèn tồn kho
        cursor.execute("INSERT INTO inventories (variant_id, store_id, quantity) VALUES (?, ?, ?)", 
                      (variant_id, store_id, 5))
        
        # Chèn đơn hàng
        cursor.execute("INSERT INTO orders (user_id, address_id, status, subtotal, shipping_fee, tax, total, payment_method, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (user_id, address_id, 'pending', 980000.00, 30000.00, 0.00, 1010000.00, 'cash', 'pending'))
        order_id = cursor.lastrowid
        
        # Chèn chi tiết đơn hàng
        cursor.execute("INSERT INTO order_items (order_id, variant_id, quantity, unit_price) VALUES (?, ?, ?, ?)", 
                      (order_id, variant_id, 1, 980000.00))
        
        conn.commit()
        print("Order inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

def calculate_avg_order_value_2025():
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    
    query = """
    WITH months AS (
        SELECT 1 AS month
        UNION ALL
        SELECT month + 1
        FROM months
        WHERE month < 12
    )
    SELECT 
        m.month,
        COALESCE(ROUND(AVG(o.subtotal), 2), 0.00) AS average_order_value
    FROM months m
    LEFT JOIN orders o 
        ON CAST(strftime('%m', o.order_date) AS INTEGER) = m.month
        AND strftime('%Y', o.order_date) = '2025'
    GROUP BY m.month
    ORDER BY m.month;
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    print("| month | average_order_value |")
    print("-" * 30)
    for row in rows:
        print(f"| {row[0]:<5} | {row[1]:<19} |")
    
    conn.close()

def calculate_churn_rate():
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    
    query = """
    WITH active_users AS (
        SELECT DISTINCT user_id
        FROM orders
        WHERE order_date BETWEEN '2024-05-12 00:00:00' AND '2024-11-12 23:59:59'
    ),
    churned_users AS (
        SELECT au.user_id
        FROM active_users au
        LEFT JOIN orders o 
            ON au.user_id = o.user_id
            AND o.order_date BETWEEN '2024-11-12 00:00:00' AND '2025-05-12 23:59:59'
        WHERE o.user_id IS NULL
    )
    SELECT 
        ROUND(
            (CAST(COUNT(cu.user_id) AS FLOAT) / (SELECT COUNT(DISTINCT user_id) FROM active_users)) * 100,
            2
        ) AS churn_rate
    FROM churned_users cu;
    """
    
    cursor.execute(query)
    row = cursor.fetchone()
    
    if row:
        print("| churn_rate |")
        print("-" * 13)
        print(f"| {row[0]:<10} |")
    
    conn.close()

def insert_sample_data():
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    
    try:
        # Chèn người dùng mới
        cursor.execute("INSERT INTO users (name, email, phone, password_hash) VALUES (?, ?, ?, ?)", 
                      ('user1', 'user1@gmail.com', '111222333', 'hashed_password'))
        user1_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO users (name, email, phone, password_hash) VALUES (?, ?, ?, ?)", 
                      ('user2', 'user2@gmail.com', '222333444', 'hashed_password'))
        user2_id = cursor.lastrowid
        
        # Chèn địa chỉ cho user1 và user2
        cursor.execute("INSERT INTO user_addresses (user_id, province, district, commune, address_detail, housing_type, is_default) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                      (user1_id, 'Hà Nội', 'Hoàn Kiếm', 'Hàng Bông', '456 Đường Hai Bà Trưng', 'nhà riêng', 1))
        address1_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO user_addresses (user_id, province, district, commune, address_detail, housing_type, is_default) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                      (user2_id, 'TP HCM', 'Quận 1', 'Bến Nghé', '789 Lê Lợi', 'nhà riêng', 1))
        address2_id = cursor.lastrowid
        
        # Chèn đơn hàng cho user1 trong 6 tháng trước (10/2024)
        cursor.execute("INSERT INTO orders (user_id, address_id, order_date, status, subtotal, shipping_fee, tax, total, payment_method, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (user1_id, address1_id, '2024-10-15 10:00:00', 'delivered', 600000.00, 20000.00, 0.00, 620000.00, 'cash', 'paid'))
        
        # Chèn đơn hàng cho user2 trong 6 tháng trước (09/2024)
        cursor.execute("INSERT INTO orders (user_id, address_id, order_date, status, subtotal, shipping_fee, tax, total, payment_method, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (user2_id, address2_id, '2024-09-20 12:00:00', 'delivered', 800000.00, 20000.00, 0.00, 820000.00, 'cash', 'paid'))
        
        # Chèn đơn hàng cho user2 trong 6 tháng gần đây (02/2025)
        cursor.execute("INSERT INTO orders (user_id, address_id, order_date, status, subtotal, shipping_fee, tax, total, payment_method, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                      (user2_id, address2_id, '2025-02-10 15:00:00', 'pending', 1200000.00, 30000.00, 0.00, 1230000.00, 'cash', 'pending'))
        
        conn.commit()
        print("Sample data inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    #insert_assessment_order()
    #calculate_avg_order_value_2025()
    #insert_sample_data()
    calculate_churn_rate()