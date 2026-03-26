from database.db import get_db_connection

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    conn.close()
    return user

def get_user_by_identifier(identifier):
    """Return a user whose username, email, or phone matches identifier."""
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username=? OR email=? OR phone=?',
        (identifier, identifier, identifier)
    ).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT id, username, email, password, fullname, phone, created_at FROM users WHERE id=?', (user_id,)).fetchone()
    conn.close()
    return user

def create_user(username, email, hashed_password, fullname, phone, created_at):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO users (username, email, password, fullname, phone, created_at) VALUES (?, ?, ?, ?, ?, ?)',
             (username, email, hashed_password, fullname, phone, created_at))
    conn.commit()
    conn.close()

def get_all_users(search=None, date_joined=None, page=1, limit=2):
    conn = get_db_connection()
    c = conn.cursor()
    query = 'SELECT id, username, email, password, fullname, phone, created_at FROM users WHERE 1=1'
    count_query = 'SELECT COUNT(*) FROM users WHERE 1=1'
    params = []
    
    if search:
        clause = ' AND (fullname LIKE ? OR username LIKE ? OR email LIKE ? OR phone LIKE ?)'
        query += clause
        count_query += clause
        params += [f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%']
    if date_joined:
        clause = ' AND date(created_at) = ?'
        query += clause
        count_query += clause
        params.append(date_joined)
        
    c.execute(count_query, params)
    total_count = c.fetchone()[0]
        
    query += ' ORDER BY created_at DESC'
    if limit:
        query += ' LIMIT ? OFFSET ?'
        params.extend([limit, (page - 1) * limit])
        
    c.execute(query, params)
    users = c.fetchall()
    conn.close()
    return users, total_count

def update_user(user_id, fullname, email, phone, hashed_password=None):
    conn = get_db_connection()
    c = conn.cursor()
    if hashed_password:
        c.execute('UPDATE users SET fullname=?, email=?, phone=?, password=? WHERE id=?',
                 (fullname, email, phone, hashed_password, user_id))
    else:
        c.execute('UPDATE users SET fullname=?, email=?, phone=? WHERE id=?',
                 (fullname, email, phone, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id=?', (user_id,))
    conn.commit()
    conn.close()

def get_total_users():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    total = c.fetchone()[0]
    conn.close()
    return total

def get_user_fullname_phone(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT fullname, phone FROM users WHERE id=?', (user_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_user_username_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT username FROM users WHERE id=?', (user_id,)).fetchone()
    conn.close()
    return user[0] if user else None

def check_phone_exists(phone, exclude_user_id=None):
    conn = get_db_connection()
    c = conn.cursor()
    if exclude_user_id:
        c.execute('SELECT 1 FROM users WHERE phone=? AND id!=?', (phone, exclude_user_id))
    else:
        c.execute('SELECT 1 FROM users WHERE phone=?', (phone,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

