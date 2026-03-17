from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
from datetime import datetime
from functools import wraps
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'vegmart_secret_key_2024'

app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATABASE = 'vegmart.db'

# Initialize Database
def init_db():
    conn = sqlite3.connect(DATABASE)
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
                  cost_price REAL, image_url TEXT, description TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                 (id INTEGER PRIMARY KEY, name TEXT, phone TEXT UNIQUE, date_added TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sales
                 (id INTEGER PRIMARY KEY, item_name TEXT, quantity REAL, price REAL, total REAL, 
                  customer_name TEXT, date TIMESTAMP)''')
    
    # Insert default items with images from reliable sources
    default_items = [
        ('tomato', 20, 10.0, 15, '/static/images/tomato.png', 'Fresh red tomatoes - Rich in vitamins and antioxidants'),
        ('brinjal', 25, 20.0, 20, '/static/images/brinjal.png', 'Fresh purple brinjal - High in fiber and nutrients'),
        ('potato', 40, 15.0, 30, '/static/images/potato.png', 'Fresh potatoes - Naturally gluten-free and filling'),
        ('mirchi', 30, 20.0, 20, '/static/images/mirchi.png', 'Fresh green chili - Spicy and flavorful addition to meals')
    ]
    
    for item in default_items:
        try:
            c.execute('INSERT INTO items (name, price, quantity, cost_price, image_url, description) VALUES (?, ?, ?, ?, ?, ?)', item)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()

init_db()

# Login Required Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_type') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_type' in session:
        if session['user_type'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif session['user_type'] == 'customer':
            return redirect(url_for('customer_shop'))
    return redirect(url_for('landing'))

@app.route('/landing')
def landing():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM items LIMIT 6')
    featured_items = c.fetchall()
    conn.close()
    
    return render_template('landing.html', featured_items=featured_items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        
        if role == 'customer':
            username = request.form.get('username')
            password = request.form.get('password')
            
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username=?', (username,))
            user = c.fetchone()
            conn.close()
            
            if user and check_password_hash(user[3], password):
                session['user_type'] = 'customer'
                session['username'] = user[1]
                session['user_id'] = user[0]
                flash('Login successful!', 'success')
                return redirect(url_for('customer_shop'))
            else:
                flash('Invalid username or password', 'error')
        
        elif role == 'admin':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username == 'admin' and password == 'Admin@123':
                session['user_type'] = 'admin'
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    import re
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        phone    = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side validation
        if not fullname or re.search(r'[0-9!@#$%^&*()+=\[\]{};:\'"<>,?/\\|`~]', fullname):
            flash('Full name must contain only letters and spaces', 'error')
            return redirect(url_for('register'))

        if not re.match(r'^[a-zA-Z0-9_]{3,}$', username):
            flash('Username must be at least 3 alphanumeric characters', 'error')
            return redirect(url_for('register'))

        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            flash('Please enter a valid email address', 'error')
            return redirect(url_for('register'))

        if not re.match(r'^[0-9]{10}$', phone):
            flash('Phone number must be exactly 10 digits', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))

        pw_ok = (len(password) >= 8 and re.search(r'[A-Z]', password)
                 and re.search(r'[a-z]', password) and re.search(r'[0-9]', password)
                 and re.search(r'[^a-zA-Z0-9]', password))
        if not pw_ok:
            flash('Password must be 8+ characters with uppercase, lowercase, number & special character', 'error')
            return redirect(url_for('register'))

        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            hashed_password = generate_password_hash(password)
            c.execute('INSERT INTO users (username, email, password, fullname, phone, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                     (username, email, hashed_password, fullname, phone, datetime.now()))
            conn.commit()
            conn.close()
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('landing'))

# Admin Routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]

    c.execute('SELECT COUNT(*) FROM sales')
    total_sales_count = c.fetchone()[0]

    c.execute('SELECT SUM(total) FROM sales')
    total_revenue = c.fetchone()[0] or 0

    c.execute('SELECT COUNT(*) FROM items')
    total_items = c.fetchone()[0]

    # Weekly bar chart: top vegetables by quantity sold in last 7 days
    c.execute('''
        SELECT item_name, SUM(quantity) as total_qty FROM sales
        WHERE date >= datetime('now', '-7 days')
        GROUP BY item_name ORDER BY total_qty DESC LIMIT 5
    ''')
    bar_rows = c.fetchall()
    bar_labels = [r[0].title() for r in bar_rows]
    bar_data   = [round(float(r[1]), 2) for r in bar_rows]

    # Weekly line chart: daily total revenue for last 7 days
    c.execute('''
        SELECT date(date) as day, SUM(total) FROM sales
        WHERE date >= datetime('now', '-7 days')
        GROUP BY day ORDER BY day ASC
    ''')
    line_rows = c.fetchall()
    line_labels = [r[0] for r in line_rows]
    line_data   = [round(float(r[1]), 2) for r in line_rows]

    conn.close()

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_sales_count=total_sales_count,
                           total_revenue=total_revenue,
                           total_items=total_items,
                           bar_labels=bar_labels, bar_data=bar_data,
                           line_labels=line_labels, line_data=line_data)

@app.route('/admin/add-item', methods=['GET', 'POST'])
@login_required
@admin_required
def add_item():
    if request.method == 'POST':
        try:
            name = request.form.get('name').lower()
            price = float(request.form.get('price'))
            quantity = float(request.form.get('quantity'))
            cost_price = float(request.form.get('cost_price'))
            description = request.form.get('description')
            
            image_url = ''
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_url = f'/static/uploads/{filename}'
            
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            c.execute('INSERT INTO items (name, price, quantity, cost_price, image_url, description) VALUES (?, ?, ?, ?, ?, ?)',
                     (name, price, quantity, cost_price, image_url, description))
            conn.commit()
            conn.close()
            
            flash('Item added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except sqlite3.IntegrityError:
            flash('Item already exists', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    return render_template('add_item.html')

@app.route('/admin/modify-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def modify_item(item_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    if request.method == 'POST':
        try:
            price = float(request.form.get('price'))
            quantity = float(request.form.get('quantity'))
            cost_price = float(request.form.get('cost_price'))
            description = request.form.get('description')
            
            c.execute('SELECT image_url FROM items WHERE id=?', (item_id,))
            image_url = c.fetchone()[0]
            
            if 'image' in request.files:
                file = request.files['image']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_url = f'/static/uploads/{filename}'
            
            c.execute('UPDATE items SET price=?, quantity=?, cost_price=?, image_url=?, description=? WHERE id=?',
                     (price, quantity, cost_price, image_url, description, item_id))
            conn.commit()
            conn.close()
            
            flash('Item modified successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    c.execute('SELECT * FROM items WHERE id=?', (item_id,))
    item = c.fetchone()
    conn.close()
    
    return render_template('modify_item.html', item=item)

@app.route('/admin/remove-item/<int:item_id>')
@login_required
@admin_required
def remove_item(item_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id=?', (item_id,))
    conn.commit()
    conn.close()
    
    flash('Item removed successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/inventory')
@login_required
@admin_required
def admin_inventory():
    search   = request.args.get('search', '').strip()
    price_min = request.args.get('price_min', '')
    price_max = request.args.get('price_max', '')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    query = 'SELECT * FROM items WHERE 1=1'
    params = []
    if search:
        query += ' AND (name LIKE ? OR description LIKE ?)'
        params += [f'%{search}%', f'%{search}%']
    if price_min:
        query += ' AND price >= ?'
        params.append(float(price_min))
    if price_max:
        query += ' AND price <= ?'
        params.append(float(price_max))
    query += ' ORDER BY name'
    c.execute(query, params)
    items = c.fetchall()
    conn.close()
    return render_template('admin_inventory.html', items=items,
                           search=search, price_min=price_min, price_max=price_max)

@app.route('/admin/customers')
@login_required
@admin_required
def admin_customers():
    search = request.args.get('search', '').strip()
    filter_date = request.args.get('date', '').strip()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    query = 'SELECT * FROM customers WHERE 1=1'
    params = []
    if search:
        query += ' AND (name LIKE ? OR phone LIKE ?)'
        params += [f'%{search}%', f'%{search}%']
    if filter_date:
        query += ' AND date_added >= ? AND date_added <= ?'
        params.extend([filter_date + ' 00:00:00', filter_date + ' 23:59:59'])
    query += ' ORDER BY date_added DESC'
    c.execute(query, params)
    customers = c.fetchall()
    conn.close()
    return render_template('admin_customers.html', customers=customers,
                           search=search, filter_date=filter_date)

@app.route('/admin/sales')
@login_required
@admin_required
def admin_sales():
    search = request.args.get('search', '').strip()
    filter_date = request.args.get('date', '').strip()
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    query = 'SELECT * FROM sales WHERE 1=1'
    params = []
    if search:
        query += ' AND (item_name LIKE ? OR customer_name LIKE ?)'
        params += [f'%{search}%', f'%{search}%']
    if filter_date:
        query += ' AND date >= ? AND date <= ?'
        params.extend([filter_date + ' 00:00:00', filter_date + ' 23:59:59'])
    query += ' ORDER BY date DESC'
    c.execute(query, params)
    sales = c.fetchall()
    c.execute('SELECT SUM(total) FROM sales WHERE 1=1' + query.replace('SELECT * FROM sales WHERE 1=1', '').replace('ORDER BY date DESC', ''), params)
    total_sales = c.fetchone()[0] or 0
    conn.close()
    return render_template('admin_sales.html', sales=sales, total_sales=total_sales,
                           search=search, filter_date=filter_date)

# Customer Routes
@app.route('/shop')
@login_required
def customer_shop():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = c.fetchall()
    conn.close()
    
    return render_template('customer_shop.html', items=items)

@app.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    cart_items = []
    total = 0
    
    for item_id, qty in cart.items():
        c.execute('SELECT * FROM items WHERE id=?', (int(item_id),))
        item = c.fetchone()
        if item:
            item_total = item[2] * qty
            cart_items.append({
                'id': item[0],
                'name': item[1],
                'price': item[2],
                'quantity': qty,
                'total': item_total,
                'image_url': item[5]
            })
            total += item_total
    
    conn.close()
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = float(data.get('quantity', 0))
    
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE id=?', (item_id,))
    item = c.fetchone()
    conn.close()
    
    if not item or item[3] < quantity:
        return jsonify({'success': False, 'message': 'Insufficient stock'})
    
    cart = session.get('cart', {})
    item_id_str = str(item_id)
    
    if item_id_str in cart:
        cart[item_id_str] += quantity
    else:
        cart[item_id_str] = quantity
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'success': True, 'message': f'Added {quantity} kg to cart'})

@app.route('/remove-from-cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart = session.get('cart', {})
    cart.pop(str(item_id), None)
    session['cart'] = cart
    session.modified = True
    
    return redirect(url_for('view_cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Always pull name & phone from the registered user record
    user_id = session.get('user_id')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT fullname, phone FROM users WHERE id=?', (user_id,))
    user_row = c.fetchone()
    conn.close()
    name  = user_row[0] if user_row and user_row[0] else session.get('username', '')
    phone = user_row[1] if user_row and user_row[1] else ''

    if request.method == 'POST':
        cart = session.get('cart', {})
        if not cart:
            flash('Your cart is empty', 'error')
            return redirect(url_for('customer_shop'))

        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()

            c.execute('INSERT OR IGNORE INTO customers (name, phone, date_added) VALUES (?, ?, ?)',
                     (name, phone, datetime.now()))

            total_amount = 0
            for item_id, qty in cart.items():
                c.execute('SELECT * FROM items WHERE id=?', (int(item_id),))
                item = c.fetchone()
                if item:
                    item_total = item[2] * qty
                    c.execute('INSERT INTO sales (item_name, quantity, price, total, customer_name, date) VALUES (?, ?, ?, ?, ?, ?)',
                             (item[1], qty, item[2], item_total, name, datetime.now()))
                    new_qty = item[3] - qty
                    c.execute('UPDATE items SET quantity=? WHERE id=?', (new_qty, item[0]))
                    total_amount += item_total

            conn.commit()
            conn.close()

            session['cart'] = {}
            session.modified = True
            flash(f'🎉 Order placed! Thank you {name}. Total: ₹{total_amount:.2f}', 'success')
            return redirect(url_for('customer_shop'))

        except Exception as e:
            flash(f'Error processing order: {str(e)}', 'error')
            return redirect(url_for('checkout'))

    cart = session.get('cart', {})
    if not cart:
        flash('Cart is empty', 'warning')
        return redirect(url_for('customer_shop'))
    
    return render_template('checkout.html', user_name=name, user_phone=phone)

@app.route('/my-orders')
@login_required
def my_orders():
    user_id = session.get('user_id')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    # Get fullname from users table for matching sales records
    c.execute('SELECT fullname FROM users WHERE id=?', (user_id,))
    user_row = c.fetchone()
    customer_name = user_row[0] if user_row and user_row[0] else session.get('username', '')
    # Fetch all orders for this customer, newest first
    c.execute('''SELECT item_name, quantity, price, total, date 
                 FROM sales WHERE customer_name=? ORDER BY date DESC''', (customer_name,))
    orders = c.fetchall()
    conn.close()
    return render_template('my_orders.html', orders=orders, customer_name=customer_name)

@app.route('/api/cart-total')
@login_required
def api_cart_total():
    cart = session.get('cart', {})
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    total = 0
    for item_id, qty in cart.items():
        c.execute('SELECT price FROM items WHERE id=?', (int(item_id),))
        row = c.fetchone()
        if row:
            total += row[0] * qty
    conn.close()
    return jsonify({'total': total})

@app.route('/api/items')
def api_items():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = c.fetchall()
    conn.close()
    
    return jsonify([{
        'id': item[0],
        'name': item[1],
        'price': item[2],
        'quantity': item[3],
        'image_url': item[5]
    } for item in items])

if __name__ == '__main__':
    app.run(debug=True)
