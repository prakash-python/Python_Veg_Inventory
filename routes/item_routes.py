from flask import Blueprint, render_template, request, session, redirect, url_for, flash, current_app
import os
from werkzeug.utils import secure_filename
from datetime import datetime

from utils.helpers import login_required, admin_required
from utils.file_upload import allowed_file
from models.item import (
    get_all_items_admin, get_item_by_id, insert_item, update_item, delete_item, get_item_name_by_id
)

item_bp = Blueprint('item', __name__)

@item_bp.route('/admin/add-item', methods=['GET', 'POST'])
@login_required
@admin_required
def add_item():
    if request.method == 'POST':
        try:
            name = request.form.get('name').strip().lower()
            price = float(request.form.get('price'))
            quantity = float(request.form.get('quantity'))
            cost_price = float(request.form.get('cost_price'))
            description = request.form.get('description')

            # Handle image upload
            image_file = request.files.get('image')
            
            if image_file and image_file.filename and allowed_file(image_file.filename):
                ext = image_file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f"{name}.{ext}")
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                image_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                image_url = f'/static/images/{filename}'
            else:
                image_url = ''  # No image — templates will show a CSS avatar

            creator = session.get('username', 'admin')
            insert_item(name, price, quantity, cost_price, image_url, description, datetime.now(), creator)

            flash('Item added successfully!', 'success')
            return redirect(url_for('item.admin_inventory'))
        except Exception as e:
            if 'UNIQUE constraint' in str(e):
                flash('Item with this name already exists', 'error')
            else:
                flash(f'Error: {str(e)}', 'error')

    return render_template('add_item.html')

@item_bp.route('/admin/modify-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def modify_item(item_id):
    if request.method == 'POST':
        try:
            price      = float(request.form.get('price'))
            quantity   = float(request.form.get('quantity'))
            cost_price = float(request.form.get('cost_price'))
            description = request.form.get('description')

            # Handle image upload — keep existing if no new file chosen
            image_file = request.files.get('image')
                
            if image_file and image_file.filename and allowed_file(image_file.filename):
                # Fetch item name for filename
                item_name = get_item_name_by_id(item_id) or str(item_id)

                ext = image_file.filename.rsplit('.', 1)[1].lower()
                filename = secure_filename(f"{item_name}.{ext}")
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
                image_file.save(save_path)
                image_url = f'/static/images/{filename}'
            else:
                image_url = request.form.get('existing_image_url', '')

            update_item(item_id, price, quantity, cost_price, image_url, description)

            flash('Item modified successfully!', 'success')
            return redirect(url_for('item.admin_inventory'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

    item = get_item_by_id(item_id)
    return render_template('modify_item.html', item=item)

@item_bp.route('/admin/remove-item/<int:item_id>')
@login_required
@admin_required
def remove_item(item_id):
    delete_item(item_id)
    flash('Item removed successfully!', 'success')
    return redirect(url_for('item.admin_inventory'))

@item_bp.route('/admin/inventory', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_inventory():
    import math
    if request.method == 'POST':
        search = request.form.get('search', '').strip()
        price_type = request.form.get('price_type', 'selling')
        price_range = request.form.get('price_range', '')
        date_created = request.form.get('date_created', '')
        page = 1
    else:
        search = request.args.get('search', '').strip()
        price_type = request.args.get('price_type', 'selling')
        price_range = request.args.get('price_range', '')
        date_created = request.args.get('date_created', '')
        page = request.args.get('page', 1, type=int)
    
    items, total_count = get_all_items_admin(search, price_type, price_range, date_created, page=page)
    total_pages = math.ceil(total_count / 2) if total_count > 0 else 1

    return render_template('admin_inventory.html', items=items,
                           search=search, price_type=price_type, 
                           price_range=price_range, date_created=date_created,
                           page=page, total_pages=total_pages, total_count=total_count)
