from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.models import User, StaffProfile, Trek, Booking
from app.extensions import db, bcrypt
from datetime import datetime

staff_bp = Blueprint('staff', __name__)


def staff_required():
    """Return True if session user is an approved Staff member."""
    return session.get('role') == 'Staff'


def get_current_staff():
    """Return the logged-in staff user or None."""
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


# ─── Dashboard ────────────────────────────────────────────────────────────────

@staff_bp.route('/dashboard')
def dashboard():
    if not staff_required():
        flash('Please log in as Staff.', 'danger')
        return redirect(url_for('auth.login'))

    staff_user = get_current_staff()
    # Only treks assigned to this staff member
    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff_user.id).all()

    # Count registered (non-cancelled) trekkers per trek
    trek_data = []
    for t in assigned_treks:
        count = Booking.query.filter_by(trek_id=t.id).filter(Booking.status != 'Cancelled').count()
        trek_data.append({'trek': t, 'trekker_count': count})

    return render_template('staff/dashboard.html', staff_user=staff_user, trek_data=trek_data)


# ─── Profile ─────────────────────────────────────────────────────────────────

@staff_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not staff_required():
        return redirect(url_for('auth.login'))

    staff_user = get_current_staff()
    profile = staff_user.staff_profile

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        contact = request.form.get('contact_details', '').strip()
        new_password = request.form.get('new_password', '').strip()

        # Check unique username/email (excluding self)
        if User.query.filter(User.username == username, User.id != staff_user.id).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('staff.profile'))
        if User.query.filter(User.email == email, User.id != staff_user.id).first():
            flash('Email already in use.', 'danger')
            return redirect(url_for('staff.profile'))

        staff_user.username = username
        staff_user.email = email
        if profile:
            profile.contact_details = contact
        if new_password:
            staff_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('staff.profile'))

    return render_template('staff/profile.html', staff_user=staff_user, profile=profile)


# ─── Trek Detail ─────────────────────────────────────────────────────────────

@staff_bp.route('/treks/<int:trek_id>')
def trek_detail(trek_id):
    if not staff_required():
        return redirect(url_for('auth.login'))

    staff_user = get_current_staff()
    trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=staff_user.id).first_or_404()
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    return render_template('staff/trek_detail.html', trek=trek, bookings=bookings, staff_user=staff_user)


# ─── Update Available Slots ──────────────────────────────────────────────────

@staff_bp.route('/treks/<int:trek_id>/update-slots', methods=['POST'])
def update_slots(trek_id):
    if not staff_required():
        return redirect(url_for('auth.login'))

    staff_user = get_current_staff()
    trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=staff_user.id).first_or_404()

    try:
        new_slots = int(request.form.get('available_slots', 0))
        if new_slots < 0:
            flash('Slots cannot be negative.', 'danger')
        else:
            trek.available_slots = new_slots
            db.session.commit()
            flash('Available slots updated.', 'success')
    except ValueError:
        flash('Invalid value for slots.', 'danger')

    return redirect(url_for('staff.trek_detail', trek_id=trek_id))


# ─── Update Trek Status (Open / Closed) ─────────────────────────────────────

@staff_bp.route('/treks/<int:trek_id>/update-status', methods=['POST'])
def update_status(trek_id):
    if not staff_required():
        return redirect(url_for('auth.login'))

    staff_user = get_current_staff()
    trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=staff_user.id).first_or_404()

    new_status = request.form.get('status')
    allowed = ['Open', 'Closed']
    if new_status in allowed:
        trek.status = new_status
        db.session.commit()
        flash(f'Trek status set to {new_status}.', 'success')
    else:
        flash('Invalid status value.', 'danger')

    return redirect(url_for('staff.trek_detail', trek_id=trek_id))


# ─── Update Trek Phase (Started / Ongoing / Completed) ──────────────────────

@staff_bp.route('/treks/<int:trek_id>/update-phase', methods=['POST'])
def update_phase(trek_id):
    if not staff_required():
        return redirect(url_for('auth.login'))

    staff_user = get_current_staff()
    trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=staff_user.id).first_or_404()

    new_phase = request.form.get('phase')
    allowed = ['Started', 'Ongoing', 'Completed']
    if new_phase in allowed:
        trek.status = new_phase
        # When trek is completed, mark all active bookings as Completed
        if new_phase == 'Completed':
            Booking.query.filter_by(trek_id=trek.id, status='Booked').update({'status': 'Completed'})
        db.session.commit()
        flash(f'Trek marked as {new_phase}.', 'success')
    else:
        flash('Invalid phase value.', 'danger')

    return redirect(url_for('staff.trek_detail', trek_id=trek_id))


# ─── Participants List ────────────────────────────────────────────────────────

@staff_bp.route('/treks/<int:trek_id>/participants')
def participants(trek_id):
    if not staff_required():
        return redirect(url_for('auth.login'))

    staff_user = get_current_staff()
    trek = Trek.query.filter_by(id=trek_id, assigned_staff_id=staff_user.id).first_or_404()
    bookings = Booking.query.filter_by(trek_id=trek_id).order_by(Booking.booking_date.desc()).all()
    return render_template('staff/participants.html', trek=trek, bookings=bookings, staff_user=staff_user)
