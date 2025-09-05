from flask import Flask
from application.config import Config
from application.database import db
from application.models import User
from application.controllers import *

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():
        # Create all tables
        db.create_all()

        # Create admin if not exists
        admin = User.query.filter_by(type='admin').first()
        if not admin:
            admin_user = User(
                username='Admin123',
                email='admin@user.com',
                password='admin143',  # Will be hashed automatically
                address='chpet',
                pincode=522616,
                phone_number=1234567890,
                type='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created.")
        else:
            print("Admin already exists.")

    return app
from application.controllers import register_routes
# Initialize the app
app = create_app()
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
