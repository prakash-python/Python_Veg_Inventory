from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import re
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from utils.helpers import login_required, admin_required
from models.user import (
    get_user_by_username, create_user, get_all_users, get_user_by_id,
    update_user, delete_user, check_phone_exists
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')
        
        if role == 'customer':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = get_user_by_username(username)
            
            if user and check_password_hash(user['password'], password):
                session['user_type'] = 'customer'
                session['username'] = user['username']
                session['user_id'] = user['id']
                return redirect(url_for('customer.customer_shop'))
            else:
                flash('Invalid username or password', 'error')
        
        elif role == 'admin':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if username == 'admin' and password == 'Admin@123':
                session['user_type'] = 'admin'
                session['username'] = 'admin'
                return redirect(url_for('sales.admin_dashboard'))
            else:
                flash('Invalid admin credentials', 'error')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip()
        phone    = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Server-side validation
        if not fullname or re.search(r'[0-9!@#$%^&*()+=\[\]{};:\'"<>,?/\\|`~]', fullname):
            return render_template('register.html', error='Full name must contain only letters and spaces', **request.form)

        if not re.match(r'^[a-zA-Z0-9_]{3,}$', username):
            return render_template('register.html', error='Username must be at least 3 alphanumeric characters', **request.form)

        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return render_template('register.html', error='Please enter a valid email address', **request.form)

        if not re.match(r'^[0-9]{10}$', phone):
            return render_template('register.html', error='Phone number must be exactly 10 digits', **request.form)

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match', **request.form)

        pw_ok = (len(password) >= 8 and re.search(r'[A-Z]', password)
                 and re.search(r'[a-z]', password) and re.search(r'[0-9]', password)
                 and re.search(r'[^a-zA-Z0-9]', password))
        if not pw_ok:
            return render_template('register.html', error='Password must be 8+ characters with uppercase, lowercase, number & special character', **request.form)

        if check_phone_exists(phone):
            return render_template('register.html', error='This phone number is already registered. Please login to your account instead.', **request.form)

        try:
            hashed_password = generate_password_hash(password)
            create_user(username, email, hashed_password, fullname, phone, datetime.now())
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            if 'UNIQUE constraint' in str(e):
                return render_template('register.html', error='Username or email already exists', **request.form)
            else:
                return render_template('register.html', error=f'Error: {str(e)}', **request.form)

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('customer.landing'))

# --- ADMIN USER MANAGEMENT ---

@auth_bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_users():
    import math
    if request.method == 'POST':
        search = request.form.get('search', '').strip()
        date_joined = request.form.get('date_joined', '')
        page = 1
    else:
        search = request.args.get('search', '').strip()
        date_joined = request.args.get('date_joined', '')
        page = request.args.get('page', 1, type=int)
        
    users, total_count = get_all_users(search, date_joined, page=page)
    total_pages = math.ceil(total_count / 2) if total_count > 0 else 1
    
    return render_template('admin_users.html', users=users, 
                           search=search, date_joined=date_joined,
                           page=page, total_pages=total_pages, total_count=total_count)

@auth_bp.route('/admin/add-user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '')
        username = request.form.get('username', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        password = request.form.get('password', '')
        
        user_data = {'fullname': fullname, 'username': username, 'email': email, 'phone': phone}
        
        if check_phone_exists(phone):
            return render_template('user_form.html', is_edit=False, error='This phone number is already registered to another user.', user=user_data)
        
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        try:
            create_user(username, email, hashed_password, fullname, phone, datetime.now())
            flash('System user created successfully!', 'success')
            return redirect(url_for('auth.admin_users'))
        except Exception as e:
            if 'UNIQUE constraint' in str(e):
                return render_template('user_form.html', is_edit=False, error='Username or Email already exists!', user=user_data)
            else:
                return render_template('user_form.html', is_edit=False, error=f'Error: {str(e)}', user=user_data)
            
    return render_template('user_form.html', is_edit=False, user=None)

@auth_bp.route('/admin/modify-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def modify_user(user_id):
    if request.method == 'POST':
        fullname = request.form.get('fullname', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        password = request.form.get('password', '')
        
        user_data = get_user_by_id(user_id) # Need original to pass back username/etc if failing
        
        if check_phone_exists(phone, exclude_user_id=user_id):
            updated_user = dict(user_data)
            updated_user.update({'fullname': fullname, 'email': email, 'phone': phone})
            return render_template('user_form.html', is_edit=True, error='This phone number is already registered to another user.', user=updated_user)
        
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256') if password else None
            update_user(user_id, fullname, email, phone, hashed_password)
            flash('User account updated successfully!', 'success')
            return redirect(url_for('auth.admin_users'))
        except Exception as e:
            updated_user = dict(user_data)
            updated_user.update({'fullname': fullname, 'email': email, 'phone': phone})
            return render_template('user_form.html', is_edit=True, error=f'Update Error: {str(e)}', user=updated_user)
        
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('auth.admin_users'))
        
    return render_template('user_form.html', is_edit=True, user=user)

@auth_bp.route('/admin/remove-user/<int:user_id>')
@login_required
@admin_required
def remove_user(user_id):
    user = get_user_by_id(user_id)
    
    # Prevent deletion of the currently logged-in admin
    if user and user['username'] == session.get('username'):
        flash('Action blocked! You cannot delete your own active account.', 'error')
    else:
        delete_user(user_id)
        flash('User deleted successfully.', 'success')
        
    return redirect(url_for('auth.admin_users'))
