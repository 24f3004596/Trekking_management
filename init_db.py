from app import create_app
from app.extensions import db, bcrypt
from app.models import User
import os

app = create_app()

def init_database():
    with app.app_context():
        # Ensure instance folder exists
        os.makedirs(app.instance_path, exist_ok=True)
        
        # Create all tables
        db.create_all()
        print("Database tables created successfully.")

        # Check if Admin user exists
        admin_email = 'admin@trek.com'
        admin = User.query.filter_by(email=admin_email).first()
        
        if not admin:
            # Create the Admin user
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            new_admin = User(
                username='SuperAdmin',
                email=admin_email,
                password_hash=hashed_password,
                role='Admin',
                is_active_user=True
            )
            db.session.add(new_admin)
            db.session.commit()
            print(f"Admin user created: Email={admin_email}, Password=admin123")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    init_database()
