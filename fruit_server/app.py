from flask import Flask, jsonify, request
from flask_cors import CORS
import time
import re
import sqlite3
import json

app = Flask(__name__)
# 允許來自前端的跨域請求
CORS(app, resources={r"/api/*": {"origins": "*"}})

DB_PATH = 'fruit_store.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 會員資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            account TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            lastName TEXT DEFAULT '',
            firstName TEXT DEFAULT '',
            phone TEXT DEFAULT '',
            address TEXT DEFAULT '',
            is_remembered INTEGER DEFAULT 0,
            cart_items TEXT DEFAULT '[]'
        )
    ''')
    
    # 水果商品資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fruits (
            fruit_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price INTEGER NOT NULL,
            unit TEXT NOT NULL,
            origin TEXT NOT NULL,
            image_url TEXT NOT NULL
        )
    ''')
    
    # 訂單資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            account TEXT NOT NULL,
            recipientName TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            items TEXT NOT NULL,
            totalPrice INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 🚀 修改：更新水果種子資料中的名稱 (北蕉(香蕉) -> 香蕉、集集山蕉 -> 山蕉)
    fruits_seed = [
        ("M001", "愛文芒果", "當季主打", 120, "斤", "屏東枋山", "https://images.unsplash.com/photo-1553279768-865429fa0078?w=500"),
        ("M002", "金鑽鳳梨", "當季主打", 70, "斤", "高雄大樹", "https://images.unsplash.com/photo-1550258987-190a2d41a8ba?w=500"),
        ("M003", "大西瓜", "當季主打", 25, "斤", "花蓮玉里", "https://images.unsplash.com/photo-1587049352846-4a222e784d38?w=500"),
        ("M004", "荔枝(去枝葉)", "當季主打", 180, "斤", "高雄大樹", "https://shoplineimg.com/61efa511d8ebda00312cdc21/644fdc66e555d5001d11af46/800x.jpg?"),
        ("M005", "百香果", "當季主打", 110, "斤", "南投埔里", "https://pgw.udn.com.tw/gw/photo.php?u=/photo/2024/08/12/realtime/30254397.jpg&x=0&y=0&sw=0&sh=0&exp=3600"),
        ("M006", "香蕉", "當季主打", 45, "斤", "屏東萬巒", "https://images.unsplash.com/photo-1528825871115-3581a5387919?w=500"), # 🌟 已修改
        ("L001", "愛文芒果", "在地小農", 120, "斤", "屏東枋山", "https://images.unsplash.com/photo-1553279768-865429fa0078?w=500"),
        ("L002", "荔枝(去枝葉)", "在地小農", 180, "斤", "高雄大樹", "https://shoplineimg.com/61efa511d8ebda00312cdc21/644fdc66e555d5001d11af46/800x.jpg?"),
        ("L003", "山蕉", "在地小農", 55, "斤", "南投集集", "https://images.unsplash.com/photo-1528825871115-3581a5387919?w=500")  # 🌟 已修改
    ]
    
    # 🌟 注意：由於先前已經建立過資料表，INSERT OR IGNORE 會跳過重複的主鍵。
    # 為了讓名稱修改順利套用，這裡改用 REPLACE 以直接覆蓋舊的商品資料
    cursor.executemany('INSERT OR REPLACE INTO fruits VALUES (?,?,?,?,?,?,?)', fruits_seed)
        
    # 預設測試會員
    cursor.execute('SELECT COUNT(*) FROM users WHERE account = ?', ("john998@example.com",))
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO users (username, account, password, lastName, firstName, phone, address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("老約翰", "john998@example.com", "123", "老", "約翰", "0912-345-678", "123 Maple Street"))

    conn.commit()
    conn.close()

init_db()

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

# [GET] 取得水果清單
@app.route('/api/fruits', methods=['GET'])
def get_fruits():
    conn = get_db_connection()
    fruits = [dict(row) for row in conn.execute('SELECT * FROM fruits').fetchall()]
    conn.close()
    return jsonify({"success": True, "data": fruits})

# [GET] 後端自動檢查上次登入狀態
@app.route('/api/auth/auto-login', methods=['GET'])
def auto_login():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE is_remembered = 1').fetchone()
    conn.close()
    
    if user:
        user_info = dict(user)
        del user_info['password']
        user_info['cart_items'] = json.loads(user_info['cart_items'])
        return jsonify({"success": True, "user": user_info})
    return jsonify({"success": False, "message": "目前無記憶登入的會員"})

# [POST] 會員登入
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    account = data.get('username')
    password = data.get('password')

    if not account or not password:
        return jsonify({"success": False, "message": "請填寫帳號與密碼！"}), 400

    conn = get_db_connection()
    conn.execute('UPDATE users SET is_remembered = 0')
    
    user = conn.execute('SELECT * FROM users WHERE account = ? AND password = ?', (account, password)).fetchone()
    
    if user:
        conn.execute('UPDATE users SET is_remembered = 1 WHERE account = ?', (account,))
        conn.commit()
        
        user_info = dict(user)
        del user_info['password']
        user_info['cart_items'] = json.loads(user_info['cart_items'])
        conn.close()
        return jsonify({"success": True, "user": user_info})
    else:
        conn.close()
        return jsonify({"success": False, "message": "帳號或密碼錯誤！"}), 401

# [POST] 會員註冊
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    nickname = data.get('nickname', '')
    account = data.get('username', '')
    password = data.get('password', '')

    if not account or not password or not nickname:
        return jsonify({"success": False, "message": "所有欄位皆為必填！"}), 400

    if not re.match(EMAIL_REGEX, account):
        return jsonify({"success": False, "message": "註冊失敗：帳號必須是正確的電子郵件格式！"}), 400

    if not re.match(r"^[\u4e00-\u9fa5]{2,4}$", nickname):
        return jsonify({"success": False, "message": "註冊失敗：會員名稱只能輸入 2 至 4 個中文字，不可包含英文或數字！"}), 400

    if len(password) < 8 or not re.search("[a-zA-Z]", password) or not re.search("[0-9]", password):
        return jsonify({"success": False, "message": "註冊失敗：密碼必須至少 8 個字，且包含英文與數字！"}), 400

    conn = get_db_connection()
    if conn.execute('SELECT 1 FROM users WHERE account = ?', (account,)).fetchone():
        conn.close()
        return jsonify({"success": False, "message": "此帳號已被註冊！"}), 400

    conn.execute('''
        INSERT INTO users (username, account, password)
        VALUES (?, ?, ?)
    ''', (nickname, account, password))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "註冊成功！"}), 210

# [POST] 即時購物車後端 SQLite 同步
@app.route('/api/cart/sync', methods=['POST'])
def sync_cart():
    data = request.get_json()
    account = data.get('username')
    cart_items = data.get('cartItems', [])

    conn = get_db_connection()
    user_exists = conn.execute('SELECT 1 FROM users WHERE account = ?', (account,)).fetchone()
    if user_exists:
        conn.execute('UPDATE users SET cart_items = ? WHERE account = ?', (json.dumps(cart_items), account))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "購物車後端同步成功"})
    conn.close()
    return jsonify({"success": False, "message": "找不到對應會員"}), 444

# [POST] 提交訂單
@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    account = data.get('username', 'guest')
    cart_items = data.get('cartItems', [])
    recipient_name = data.get('recipientName', '')
    phone = data.get('phone', '')
    address = data.get('address')

    if not cart_items or not recipient_name or not phone or not address:
        return jsonify({"success": False, "message": "請完整填寫收件資訊！"}), 400

    if not re.match(r"^[\u4e00-\u9fa5]{2,4}$", recipient_name):
        return jsonify({"success": False, "message": "下單失敗：收件人姓名只能輸入 2 至 4 個中文字！"}), 400

    if not re.match(r"^09\d{8}$", phone):
        return jsonify({"success": False, "message": "下單失敗：聯絡電話必須是開端為 09 的 10 碼純數字！"}), 400

    conn = get_db_connection()
    
    last_name = recipient_name[0] if len(recipient_name) >= 2 else recipient_name
    first_name = recipient_name[1:] if len(recipient_name) >= 2 else ""

    conn.execute('''
        UPDATE users 
        SET phone = ?, address = ?, lastName = ?, firstName = ?, cart_items = '[]'
        WHERE account = ?
    ''', (phone, address, last_name, first_name, account))

    total_price = 0
    enhanced_items = []
    for item in cart_items:
        fruit = conn.execute('SELECT * FROM fruits WHERE fruit_id = ?', (item['fruit_id'],)).fetchone()
        if fruit:
            total_price += fruit['price'] * item['quantity']
            item_with_info = dict(item)
            item_with_info['name'] = fruit['name']
            item_with_info['unit'] = fruit['unit']
            enhanced_items.append(item_with_info)

    order_id = f"ORD_{int(time.time() * 1000)}"
    conn.execute('''
        INSERT INTO orders (order_id, account, recipientName, phone, address, items, totalPrice)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (order_id, account, recipient_name, phone, address, json.dumps(enhanced_items), total_price))
    
    conn.commit()
    conn.close()
    return jsonify({"success": True, "orderId": order_id, "totalPrice": total_price}), 201

# [POST] 會員手動登出
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    data = request.get_json()
    account = data.get('username')
    conn = get_db_connection()
    user_exists = conn.execute('SELECT 1 FROM users WHERE account = ?', (account,)).fetchone()
    if user_exists:
        conn.execute('UPDATE users SET is_remembered = 0 WHERE account = ?', (account,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "後端登出成功"})
    conn.close()
    return jsonify({"success": False, "message": "無此會員"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)