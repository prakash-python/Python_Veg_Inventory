# VEGMART - Flask Web Application

A complete vegetable inventory and billing system built with Flask and SQLite.

## Features

✅ **Admin Portal**
- Add/Modify/Remove items
- View customer list
- Track sales and revenue
- Inventory management

✅ **Customer Interface**
- Browse available vegetables
- Add items to cart
- Checkout and billing
- Customer information tracking

✅ **Database**
- SQLite for data persistence
- Automatic database initialization
- Sales tracking and reporting

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The app will start on `http://localhost:5000`

## Usage

### Admin Login
- **URL:** http://localhost:5000
- **Username:** `admin`
- **Password:** `Admin@123`

### Customer
- Click "Customer" button at login
- Browse items and add to cart
- Proceed to checkout

## Project Structure

```
Python_Veg_Inventory/
├── app.py                 # Main Flask app
├── vegmart.db            # SQLite database (auto-created)
├── requirements.txt      # Python dependencies
├── templates/            # HTML templates
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── add_item.html
│   ├── modify_item.html
│   ├── admin_customers.html
│   ├── admin_sales.html
│   ├── customer_shop.html
│   ├── cart.html
│   └── checkout.html
└── static/               # CSS and static files
    └── style.css
```

## Key Functions

### Authentication
- Admin login with credentials
- Customer mode (no login required)
- Session management

### Admin Features
- CRUD operations on items
- View customer database
- Sales analytics
- Inventory tracking

### Customer Features
- Browse all items
- Add to shopping cart
- Remove from cart
- Checkout with billing

## Database Schema

**items** table:
- id, name, price, quantity, cost_price

**customers** table:
- id, name, phone, date_added

**sales** table:
- id, item_name, quantity, price, total, customer_name, date

## Next Steps to Deploy (Live)

1. **Local Testing** - Test all features
2. **Environment Variables** - Set production config
3. **Deploy Options:**
   - **Heroku** (free tier deprecated - use Railway)
   - **Railway** (free tier available)
   - **Render** (free tier available)
   - **PythonAnywhere** (free tier)

## Production Deployment Guide

### Option 1: Railway.app (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Option 2: Render.com

1. Push code to GitHub
2. Connect GitHub to Render
3. Create new Web Service
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn app:app`

Add `gunicorn` to requirements.txt:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

## Troubleshooting

**Q: Database not found?**
A: Delete `vegmart.db` and restart - it will recreate automatically

**Q: Can't login as admin?**
A: Username is `admin`, Password is `Admin@123`

**Q: Port 5000 already in use?**
A: Change in app.py: `app.run(debug=True, port=5001)`

## Future Enhancements

- [ ] User authentication for customers
- [ ] Payment gateway integration
- [ ] Email invoices
- [ ] Mobile app
- [ ] Analytics dashboard
- [ ] Multi-branch support

---

**Built by:** Your Name
**Portfolio:** GitHub Link
