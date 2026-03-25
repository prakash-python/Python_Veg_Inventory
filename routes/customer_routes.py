from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from datetime import datetime

from utils.helpers import login_required
from models.user import get_user_fullname_phone
from models.item import (
    get_all_items, get_item_by_id, update_item_quantity, get_featured_items
)
from models.customer import insert_customer
from models.sales import insert_sale, get_customer_orders

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/')
def index():
    if 'user_type' in session:
        if session['user_type'] == 'admin':
            return redirect(url_for('sales.admin_dashboard'))
        elif session['user_type'] == 'customer':
            return redirect(url_for('customer.customer_shop'))
    return redirect(url_for('customer.landing'))

@customer_bp.route('/landing')
def landing():
    featured_items = get_featured_items(6)
    return render_template('landing.html', featured_items=featured_items)

@customer_bp.route('/shop')
@login_required
def customer_shop():
    items = get_all_items()
    return render_template('customer_shop.html', items=items)

@customer_bp.route('/cart')
@login_required
def view_cart():
    cart = session.get('cart', {})
    cart_items = []
    total = 0
    
    for item_id, qty in cart.items():
        item = get_item_by_id(int(item_id))
        if item:
            item_total = item['price'] * qty
            cart_items.append({
                'id': item['id'],
                'name': item['name'],
                'price': item['price'],
                'quantity': qty,
                'total': item_total,
                'image_url': item['image_url']
            })
            total += item_total
            
    return render_template('cart.html', cart_items=cart_items, total=total)

@customer_bp.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = float(data.get('quantity', 0))
    
    item = get_item_by_id(item_id)
    if not item or item['quantity'] < quantity:
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

@customer_bp.route('/remove-from-cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart = session.get('cart', {})
    cart.pop(str(item_id), None)
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('customer.view_cart'))

@customer_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    user_id = session.get('user_id')
    user_row = get_user_fullname_phone(user_id) if user_id else None
    name  = user_row['fullname'] if user_row and user_row['fullname'] else session.get('username', '')
    phone = user_row['phone'] if user_row and user_row['phone'] else ''

    if request.method == 'POST':
        cart = session.get('cart', {})
        if not cart:
            return redirect(url_for('customer.customer_shop'))

        try:
            insert_customer(name, phone, datetime.now())

            order_id = f"ORD-{int(datetime.now().timestamp())}"
            order_date = datetime.now()
            total_amount = 0
            
            for item_id, qty in cart.items():
                item = get_item_by_id(int(item_id))
                if item:
                    item_total = item['price'] * qty
                    insert_sale(item['name'], qty, item['price'], item_total, name, order_date, order_id)
                    new_qty = item['quantity'] - qty
                    update_item_quantity(int(item_id), new_qty)
                    total_amount += item_total

            session['cart'] = {}
            session.modified = True
            return redirect(url_for('customer.customer_shop'))

        except Exception as e:
            return redirect(url_for('customer.checkout'))

    cart = session.get('cart', {})
    if not cart:
        return redirect(url_for('customer.customer_shop'))
    
    return render_template('checkout.html', user_name=name, user_phone=phone)

@customer_bp.route('/my-orders')
@login_required
def my_orders():
    user_id = session.get('user_id')
    user_row = get_user_fullname_phone(user_id) if user_id else None
    customer_name = user_row['fullname'] if user_row and user_row['fullname'] else session.get('username', '')
    
    sales = get_customer_orders(customer_name)
    
    # Group sales by order_id
    orders_dict = {}
    for row in sales:
        item_name = row['item_name']
        qty = row['quantity']
        price = row['price']
        total = row['total']
        date_str = row['date']
        order_id = row['order_id']
        
        key = order_id if order_id else date_str
        
        if key not in orders_dict:
            orders_dict[key] = {
                'order_id': key,
                'date': date_str,
                'products': [],
                'total_amount': 0
            }
        
        orders_dict[key]['products'].append({
            'name': item_name,
            'qty': qty,
            'price': price,
            'total': total
        })
        orders_dict[key]['total_amount'] += total
        
    orders_list = list(orders_dict.values())
    orders_list.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('my_orders.html', orders=orders_list, customer_name=customer_name)

@customer_bp.route('/api/cart-total')
@login_required
def api_cart_total():
    cart = session.get('cart', {})
    total = 0
    for item_id, qty in cart.items():
        item = get_item_by_id(int(item_id))
        if item:
            total += item['price'] * qty
    return jsonify({'total': total})

@customer_bp.route('/api/items')
def api_items():
    items = get_all_items()
    return jsonify([{
        'id': item['id'],
        'name': item['name'],
        'price': item['price'],
        'quantity': item['quantity'],
        'image_url': item['image_url']
    } for item in items])
