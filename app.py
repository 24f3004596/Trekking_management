from app import create_app
from app.extensions import db, bcrypt
from app.models import User
import os

app = create_app()

def init_database():
    db_path = os.path.join(app.instance_path, 'trekking.db')
    if os.path.exists(db_path):
        return  # Database already exists, do nothing

    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db.create_all()
        
        # Check if Admin user exists
        admin_email = 'admin@gmail.com'
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

if __name__ == '__main__':
    init_database()
    app.run(debug=True)
