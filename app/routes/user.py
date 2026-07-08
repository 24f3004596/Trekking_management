from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from app.models import User, Trek, Booking
from app.extensions import db, bcrypt

user_bp = Blueprint('user', __name__)


def login_required():
    return session.get('role') == 'Trekker'


def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    return User.query.get(user_id)


# Dashboard

@user_bp.route('/dashboard')
def dashboard():
    if not login_required():
        flash('Please log in as a Trekker.', 'danger')
        return redirect(url_for('auth.login'))

    current_user = get_current_user()
    my_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    active_count = sum(1 for b in my_bookings if b.status == 'Booked')
    return render_template('user/dashboard.html', current_user=current_user,
                           my_bookings=my_bookings, active_count=active_count)


# Browse open treks with search/filter

@user_bp.route('/treks')
def treks():
    if not login_required():
        return redirect(url_for('auth.login'))

    search = request.args.get('search', '').strip()
    difficulty = request.args.get('difficulty', '').strip()
    location = request.args.get('location', '').strip()

    query = Trek.query.filter_by(status='Open')

    if search:
        query = query.filter(
            Trek.name.ilike(f'%{search}%') |
            Trek.location.ilike(f'%{search}%')
        )
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))

    available_treks = query.all()

    # Get unique locations for the filter dropdown
    all_locations = db.session.query(Trek.location).filter_by(status='Open').distinct().all()
    locations = sorted(set(loc[0] for loc in all_locations))

    return render_template('user/treks.html', treks=available_treks, search=search,
                           difficulty=difficulty, location=location, locations=locations)


# Book a trek

@user_bp.route('/treks/<int:trek_id>/book', methods=['POST'])
def book_trek(trek_id):
    if not login_required():
        return redirect(url_for('auth.login'))

    current_user = get_current_user()
    trek = Trek.query.get_or_404(trek_id)

    # Check trek is open
    if trek.status != 'Open':
        flash('This trek is not open for booking.', 'danger')
        return redirect(url_for('user.treks'))

    # Check slots available
    if trek.available_slots <= 0:
        flash('No slots available for this trek.', 'danger')
        return redirect(url_for('user.treks'))

    # Check duplicate booking
    existing = Booking.query.filter_by(user_id=current_user.id, trek_id=trek_id, status='Booked').first()
    if existing:
        flash('You have already booked this trek.', 'warning')
        return redirect(url_for('user.treks'))

    # Create booking and reduce slot
    booking = Booking(user_id=current_user.id, trek_id=trek_id, status='Booked')
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    flash('Trek booked successfully.', 'success')
    return redirect(url_for('user.my_bookings'))


# My bookings

@user_bp.route('/bookings')
def my_bookings():
    if not login_required():
        return redirect(url_for('auth.login'))

    current_user = get_current_user()
    bookings = Booking.query.filter_by(user_id=current_user.id, status='Booked').order_by(Booking.booking_date.desc()).all()
    return render_template('user/bookings.html', bookings=bookings, current_user=current_user)


# Cancel booking

@user_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    if not login_required():
        return redirect(url_for('auth.login'))

    current_user = get_current_user()
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first_or_404()

    if booking.status != 'Booked':
        flash('Only active bookings can be cancelled.', 'warning')
        return redirect(url_for('user.my_bookings'))

    booking.status = 'Cancelled'
    booking.trek.available_slots += 1
    db.session.commit()
    flash('Booking cancelled.', 'success')
    return redirect(url_for('user.my_bookings'))


# Trekking history (completed/cancelled)

@user_bp.route('/history')
def history():
    if not login_required():
        return redirect(url_for('auth.login'))

    current_user = get_current_user()
    past = Booking.query.filter(
        Booking.user_id == current_user.id,
        Booking.status.in_(['Cancelled', 'Completed'])
    ).order_by(Booking.booking_date.desc()).all()

    # Deduplicate — keep only the most recent record per trek
    seen = set()
    unique_past = []
    for b in past:
        if b.trek_id not in seen:
            seen.add(b.trek_id)
            unique_past.append(b)

    return render_template('user/history.html', bookings=unique_past, current_user=current_user)


# Profile

@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not login_required():
        return redirect(url_for('auth.login'))

    current_user = get_current_user()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '').strip()

        if User.query.filter(User.username == username, User.id != current_user.id).first():
            flash('Username already taken.', 'danger')
            return redirect(url_for('user.profile'))
        if User.query.filter(User.email == email, User.id != current_user.id).first():
            flash('Email already in use.', 'danger')
            return redirect(url_for('user.profile'))

        current_user.username = username
        current_user.email = email
        if new_password:
            current_user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('user.profile'))

    return render_template('user/profile.html', current_user=current_user)
