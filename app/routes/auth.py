from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import User, StaffProfile
from app.extensions import db, bcrypt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            # Check if active
            if not user.is_active_user:
                flash('Your account has been deactivated.', 'danger')
                return redirect(url_for('auth.login'))
                
            # Check if staff is approved
            if user.role == 'Staff':
                if user.staff_profile and user.staff_profile.status != 'Approved':
                    flash('Your staff account is pending admin approval.', 'warning')
                    return redirect(url_for('auth.login'))
            
            # Simple session login
            session['user_id'] = user.id
            session['role'] = user.role
            
            # Redirect to specific dashboard
            if user.role == 'Admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'Staff':
                return redirect(url_for('staff.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
                
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role') # 'Trekker' or 'Staff'
        
        # Simple validation
        if User.query.filter_by(email=email).first():
            flash('Email address already exists.', 'danger')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        
        new_user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            role=role
        )
        db.session.add(new_user)
        db.session.commit() # Commit to generate user ID
        
        if role == 'Staff':
            contact = request.form.get('contact_details', '')
            new_profile = StaffProfile(user_id=new_user.id, contact_details=contact, status='Pending')
            db.session.add(new_profile)
            db.session.commit()
            flash('Registration successful! Please wait for Admin approval to login.', 'success')
        else:
            flash('Registration successful! You can now login.', 'success')
            
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
