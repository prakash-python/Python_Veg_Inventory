from flask import Blueprint, render_template, request
from utils.helpers import login_required, admin_required

from models.user import get_total_users
from models.item import get_total_items
from models.sales import (
    get_total_sales_count, get_total_revenue, get_dashboard_bar_chart,
    get_dashboard_line_chart, get_dashboard_profit_rows, get_all_sales
)

sales_bp = Blueprint('sales', __name__)

@sales_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    total_users = get_total_users()
    total_sales_count = get_total_sales_count()
    total_revenue = get_total_revenue()
    total_items = get_total_items()

    bar_rows = get_dashboard_bar_chart()
    bar_labels = [r['item_name'].title() for r in bar_rows]
    bar_data   = [round(float(r['total_qty']), 2) for r in bar_rows]

    line_rows = get_dashboard_line_chart()
    line_labels = [r['day'] for r in line_rows]
    line_data   = [round(float(r['SUM(total)']), 2) for r in line_rows]

    profit_rows = get_dashboard_profit_rows()
    # Each row: (item_name, total_qty, revenue, cost_price, profit)
    total_profit = sum(float(r['profit']) for r in profit_rows)

    return render_template('admin_dashboard.html',
                           total_users=total_users,
                           total_sales_count=total_sales_count,
                           total_revenue=total_revenue,
                           total_items=total_items,
                           bar_labels=bar_labels, bar_data=bar_data,
                           line_labels=line_labels, line_data=line_data,
                           profit_rows=profit_rows, total_profit=total_profit)

@sales_bp.route('/admin/sales', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_sales():
    import math
    if request.method == 'POST':
        search = request.form.get('search', '').strip()
        date = request.form.get('date', '').strip()
        page = 1
    else:
        search = request.args.get('search', '').strip()
        date = request.args.get('date', '').strip()
        page = request.args.get('page', 1, type=int)
        
    sales, total_sales, total_count = get_all_sales(search, date, page=page)
    total_pages = math.ceil(total_count / 2) if total_count > 0 else 1
    
    return render_template('admin_sales.html', sales=sales, total_sales=total_sales,
                           search=search, date=date, page=page, total_pages=total_pages, total_count=total_count)
