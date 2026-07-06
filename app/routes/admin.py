from flask import Blueprint, render_template, session, redirect, url_for
from app.models import User

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    if session.get('role') != 'Admin':
        return redirect(url_for('auth.login'))
        
    return render_template('admin/dashboard.html')
