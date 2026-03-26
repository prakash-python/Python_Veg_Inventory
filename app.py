from flask import Flask
from config import SECRET_KEY, UPLOAD_FOLDER, MAX_CONTENT_LENGTH, PERMANENT_SESSION_LIFETIME
import os

from routes.auth_routes import auth_bp
from routes.item_routes import item_bp
from routes.sales_routes import sales_bp
from routes.customer_routes import customer_bp

# Initialize Database on app start
import database.db

app = Flask(__name__)

# Application Configuration
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
app.config['PERMANENT_SESSION_LIFETIME'] = PERMANENT_SESSION_LIFETIME

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(item_bp)
app.register_blueprint(sales_bp)
app.register_blueprint(customer_bp)

if __name__ == '__main__':
    app.run(debug=True)
