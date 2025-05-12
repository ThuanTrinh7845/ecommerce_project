import sqlite3

def init_database():
    # connect to database
    conn = sqlite3.connect("ecommerce.db")
    cursor = conn.cursor()
    
    # read and run database.sql
    with open("database.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    
    # Lưu thay đổi và đóng kết nối
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()