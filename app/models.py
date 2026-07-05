from app.extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'Admin', 'Staff', 'Trekker'
    is_active_user = db.Column(db.Boolean, default=True) # for blacklisting
    
    # Relationships
    staff_profile = db.relationship('StaffProfile', backref='user', uselist=False, cascade="all, delete-orphan")
    bookings = db.relationship('Booking', backref='user', lazy=True)
    assigned_treks = db.relationship('Trek', backref='assigned_staff', lazy=True) # If user is a staff

    def __repr__(self):
        return f"<User {self.username} - {self.role}>"

class StaffProfile(db.Model):
    __tablename__ = 'staff_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_details = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='Pending') # 'Pending', 'Approved'

    def __repr__(self):
        return f"<StaffProfile {self.user.username} - {self.status}>"

class Trek(db.Model):
    __tablename__ = 'treks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False) # 'Easy', 'Moderate', 'Hard'
    duration_days = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending') # 'Pending', 'Approved', 'Open', 'Closed', 'Completed'
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Key
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    bookings = db.relationship('Booking', backref='trek', lazy=True)

    def __repr__(self):
        return f"<Trek {self.name} - {self.status}>"

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Booked') # 'Booked', 'Cancelled', 'Completed'

    def __repr__(self):
        return f"<Booking User:{self.user_id} Trek:{self.trek_id} Status:{self.status}>"
