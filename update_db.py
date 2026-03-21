import sqlite3
from datetime import datetime
import os

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vegmart.db')

def update_existing_items():
    print(f"Connecting to database at {DATABASE}")
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Try fetching the first existing user as the admin fallback
    c.execute("SELECT username FROM users ORDER BY id ASC LIMIT 1")
    first_user = c.fetchone()
    if first_user:
        admin_user = first_user[0]
        print(f"Fetched User from DB to act as creator: '{admin_user}'")
    else:
        # Fallback if DB is 100% empty
        admin_user = 'admin'
        print("No users found in DB. Defaulting to 'admin'")
        
    current_time = datetime.now()
    
    # Update existing items where created_at or created_by is null
    c.execute(
        "UPDATE items SET created_at = ?, created_by = ? WHERE created_at IS NULL OR created_by IS NULL",
        (current_time, admin_user)
    )
    
    rows_updated = c.rowcount
    print(f"Successfully updated {rows_updated} items with creator '{admin_user}' and current timestamp.")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    update_existing_items()
