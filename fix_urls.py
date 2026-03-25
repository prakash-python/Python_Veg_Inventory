import os
import re

mapping = {
    'login': 'auth.login',
    'register': 'auth.register',
    'logout': 'auth.logout',
    'admin_users': 'auth.admin_users',
    'add_user': 'auth.add_user',
    'modify_user': 'auth.modify_user',
    'remove_user': 'auth.remove_user',

    'add_item': 'item.add_item',
    'modify_item': 'item.modify_item',
    'remove_item': 'item.remove_item',
    'admin_inventory': 'item.admin_inventory',

    'admin_dashboard': 'sales.admin_dashboard',
    'admin_sales': 'sales.admin_sales',

    'index': 'customer.index',
    'landing': 'customer.landing',
    'customer_shop': 'customer.customer_shop',
    'view_cart': 'customer.view_cart',
    'add_to_cart': 'customer.add_to_cart',
    'remove_from_cart': 'customer.remove_from_cart',
    'checkout': 'customer.checkout',
    'my_orders': 'customer.my_orders',
    'api_cart_total': 'customer.api_cart_total',
    'api_items': 'customer.api_items',
}

templates_dir = os.path.join(os.path.dirname(__file__), 'templates')

for filename in os.listdir(templates_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(templates_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content
        for old, new in mapping.items():
            # Replace url_for('old' or url_for("old"
            new_content = re.sub(r"url_for\('" + old + r"'", f"url_for('{new}'", new_content)
            new_content = re.sub(r'url_for\("' + old + r'"', f'url_for("{new}"', new_content)

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}")

print("Done.")
