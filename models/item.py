from database.db import get_db_connection

def get_total_items():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM items')
    total = c.fetchone()[0]
    conn.close()
    return total

def get_featured_items(limit=6):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM items LIMIT ?', (limit,))
    items = c.fetchall()
    conn.close()
    return items

def get_all_items_admin(search=None, price_type='selling', price_range=None, date_created=None, page=1, limit=5):
    conn = get_db_connection()
    c = conn.cursor()
    query = 'SELECT * FROM items WHERE 1=1'
    count_query = 'SELECT COUNT(*) FROM items WHERE 1=1'
    params = []
    
    if search:
        clause = ' AND (name LIKE ? OR description LIKE ?)'
        query += clause
        count_query += clause
        params += [f'%{search}%', f'%{search}%']
        
    if price_range:
        col = 'price' if price_type == 'selling' else 'cost_price'
        clause = ''
        if price_range == '0-50':
            clause = f' AND {col} BETWEEN 0 AND 50'
        elif price_range == '50-100':
            clause = f' AND {col} BETWEEN 50 AND 100'
        elif price_range == '100-500':
            clause = f' AND {col} BETWEEN 100 AND 500'
        elif price_range == '500+':
            clause = f' AND {col} >= 500'
        query += clause
        count_query += clause
            
    if date_created:
        clause = ' AND date(created_at) = ?'
        query += clause
        count_query += clause
        params.append(date_created)
        
    c.execute(count_query, params)
    total_count = c.fetchone()[0]
        
    query += ' ORDER BY name'
    if limit:
        query += ' LIMIT ? OFFSET ?'
        params.extend([limit, (page - 1) * limit])
        
    c.execute(query, params)
    items = c.fetchall()
    conn.close()
    return items, total_count

def get_all_items():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = c.fetchall()
    conn.close()
    return items

def get_item_by_id(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id=?', (item_id,)).fetchone()
    conn.close()
    return item

def get_item_price(item_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT price FROM items WHERE id=?', (item_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_item_name_by_id(item_id):
    conn = get_db_connection()
    row = conn.execute('SELECT name FROM items WHERE id=?', (item_id,)).fetchone()
    conn.close()
    return row[0] if row else None

def insert_item(name, price, quantity, cost_price, image_url, description, created_at, created_by):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO items (name, price, quantity, cost_price, image_url, description, created_at, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
             (name, price, quantity, cost_price, image_url, description, created_at, created_by))
    conn.commit()
    conn.close()

def update_item(item_id, price, quantity, cost_price, image_url, description):
    conn = get_db_connection()
    conn.execute(
        'UPDATE items SET price=?, quantity=?, cost_price=?, image_url=?, description=? WHERE id=?',
        (price, quantity, cost_price, image_url, description, item_id)
    )
    conn.commit()
    conn.close()

def update_item_quantity(item_id, new_quantity):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('UPDATE items SET quantity=? WHERE id=?', (new_quantity, item_id))
    conn.commit()
    conn.close()

def delete_item(item_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id=?', (item_id,))
    conn.commit()
    conn.close()
