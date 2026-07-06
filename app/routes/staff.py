from flask import Blueprint, render_template, session, redirect, url_for

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'Staff':
        return redirect(url_for('auth.login'))
        
    return render_template('staff/dashboard.html')
