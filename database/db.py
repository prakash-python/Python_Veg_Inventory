import sqlite3
from datetime import datetime
from config import DATABASE

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users table (for customer registration)
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT UNIQUE, 
                  password TEXT, fullname TEXT, phone TEXT, created_at TIMESTAMP)''')
    # Migration: add fullname/phone columns if they don't exist (for existing DBs)
    try:
        c.execute('ALTER TABLE users ADD COLUMN fullname TEXT')
    except:
        pass
    try:
        c.execute('ALTER TABLE users ADD COLUMN phone TEXT')
    except:
        pass
    
    # Items table with image support
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE, price REAL, quantity REAL, 
                  cost_price REAL, image_url TEXT, description TEXT, created_at TIMESTAMP, created_by TEXT)''')
    try:
        c.execute('ALTER TABLE items ADD COLUMN created_at TIMESTAMP')
    except:
        pass
    try:
        c.execute('ALTER TABLE items ADD COLUMN created_by TEXT')
    except:
        pass
    
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY, name TEXT, phone TEXT UNIQUE, date_added TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sales
                 (id INTEGER PRIMARY KEY, item_name TEXT, quantity REAL, price REAL, total REAL, 
                  customer_name TEXT, date TIMESTAMP, order_id TEXT)''')
    try:
        c.execute('ALTER TABLE sales ADD COLUMN order_id TEXT')
    except:
        pass
    
    # Insert default items with images from reliable sources
    default_items = [
        ('tomato', 20, 10.0, 15, '/static/images/tomato.png', 'Fresh red tomatoes - Rich in vitamins and antioxidants'),
        ('brinjal', 25, 20.0, 20, '/static/images/brinjal.png', 'Fresh purple brinjal - High in fiber and nutrients'),
        ('potato', 40, 15.0, 30, '/static/images/potato.png', 'Fresh potatoes - Naturally gluten-free and filling'),
        ('mirchi', 30, 20.0, 20, '/static/images/mirchi.png', 'Fresh green chili - Spicy and flavorful addition to meals')
    ]
    
    for item in default_items:
        try:
            # Default items get 'admin' and current time
            item_with_audit = item + (datetime.now(), 'admin')
            c.execute('INSERT INTO items (name, price, quantity, cost_price, image_url, description, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', item_with_audit)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

# One-time cleanup: clear any external placeholder URLs stored in DB
def clean_placeholder_urls():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE items SET image_url = '' WHERE image_url LIKE '%via.placeholder%'")
    conn.commit()
    conn.close()

init_db()
clean_placeholder_urls()
