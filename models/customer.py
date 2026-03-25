from database.db import get_db_connection

def insert_customer(name, phone, date_added):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO customers (name, phone, date_added) VALUES (?, ?, ?)',
             (name, phone, date_added))
    conn.commit()
    conn.close()
