from database.db import get_db_connection

def get_total_sales_count():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM sales')
    total = c.fetchone()[0]
    conn.close()
    return total

def get_total_revenue():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT SUM(total) FROM sales')
    total = c.fetchone()[0] or 0
    conn.close()
    return total

def get_dashboard_bar_chart():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT item_name, SUM(quantity) as total_qty FROM sales
        WHERE date >= datetime('now', '-7 days')
        GROUP BY item_name ORDER BY total_qty DESC LIMIT 5
    ''')
    bar_rows = c.fetchall()
    if not bar_rows:
        c.execute('''
            SELECT item_name, SUM(quantity) as total_qty FROM sales
            GROUP BY item_name ORDER BY total_qty DESC LIMIT 5
        ''')
        bar_rows = c.fetchall()
    conn.close()
    return bar_rows

def get_dashboard_line_chart():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT date(date) as day, SUM(total) FROM sales
        WHERE date >= datetime('now', '-7 days')
        GROUP BY day ORDER BY day ASC
    ''')
    line_rows = c.fetchall()
    if not line_rows:
        c.execute('''
            SELECT date(date) as day, SUM(total) FROM sales
            GROUP BY day ORDER BY day ASC LIMIT 30
        ''')
        line_rows = c.fetchall()
    conn.close()
    return line_rows

def get_dashboard_profit_rows():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        SELECT s.item_name,
               SUM(s.quantity)                            AS total_qty,
               SUM(s.total)                               AS revenue,
               COALESCE(i.cost_price, 0)                  AS cost_price,
               SUM(s.total) - SUM(s.quantity * COALESCE(i.cost_price, 0)) AS profit
        FROM sales s
        LEFT JOIN items i ON LOWER(s.item_name) = LOWER(i.name)
        GROUP BY s.item_name
        ORDER BY profit DESC
    ''')
    profit_rows = c.fetchall()
    conn.close()
    return profit_rows

def get_all_sales(search=None, date=None, page=1, limit=10):
    conn = get_db_connection()
    c = conn.cursor()
    
    base_query = '''
    SELECT 
        COALESCE(order_id, SUBSTR(date, 1, 16)) as grp,
        GROUP_CONCAT(item_name || ' (' || quantity || 'kg)', ', ') as items,
        SUM(quantity) as total_qty,
        SUM(total) as order_total,
        customer_name,
        MAX(date) as max_date,
        COUNT(id) as item_count
    FROM sales
    WHERE 1=1
    '''
    
    params = []
    
    if search:
        clause = ' AND (item_name LIKE ? OR customer_name LIKE ?)'
        base_query += clause
        params += [f'%{search}%', f'%{search}%']
    if date:
        clause = ' AND date LIKE ?'
        base_query += clause
        params.append(f'{date}%')
        
    group_by = ' GROUP BY grp'
    
    sum_query = f'SELECT SUM(order_total) FROM ({base_query}{group_by})'
    c.execute(sum_query, params)
    total_sales = c.fetchone()[0] or 0
    
    count_query = f'SELECT COUNT(*) FROM ({base_query}{group_by})'
    c.execute(count_query, params)
    total_count = c.fetchone()[0]
        
    query = base_query + group_by + ' ORDER BY max_date DESC'
    if limit:
        query += ' LIMIT ? OFFSET ?'
        params.extend([limit, (page - 1) * limit])
        
    c.execute(query, params)
    sales = c.fetchall()
    conn.close()
    
    return sales, total_sales, total_count

def get_customer_orders(customer_name):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT item_name, quantity, price, total, date, order_id 
                 FROM sales WHERE customer_name=? ORDER BY date DESC''', (customer_name,))
    sales = c.fetchall()
    conn.close()
    return sales

def insert_sale(item_name, quantity, price, total, customer_name, order_date, order_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO sales (item_name, quantity, price, total, customer_name, date, order_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
             (item_name, quantity, price, total, customer_name, order_date, order_id))
    conn.commit()
    conn.close()
