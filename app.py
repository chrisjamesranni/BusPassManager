import os
import logging
from datetime import datetime
from flask import Flask, redirect, url_for
from extension import db, login_manager  # Import db from extensions.py
from my_models import User

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "your_fallback_secret_key")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///bus_card.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions with the app
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Import models **AFTER** db.init_app()
with app.app_context():

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    db.create_all()
    logger.info("Database tables created")

    # Check if admin user exists, if not create one
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        from werkzeug.security import generate_password_hash
        admin = User(
            username='admin',
            email='admin@college.edu',
            password_hash=generate_password_hash('admin123'),
            role='admin',
            first_name='Admin',
            last_name='User',
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        logger.info("Admin user created")

# Register blueprints
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.student import student_bp
from routes.accountant import accountant_bp

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(staff_bp, url_prefix='/staff')
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(accountant_bp, url_prefix='/accountant')

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

logger.info("Application initialized successfully")
if __name__ == '__main__':
    app.run(debug=True)