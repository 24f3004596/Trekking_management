from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import User, StaffProfile, Trek, Booking
from app.extensions import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__)


def admin_required():
    """Returns True if the current session is an admin, else False."""
    return session.get('role') == 'Admin'


# ─── Dashboard ────────────────────────────────────────────────────────────────

@admin_bp.route('/dashboard')
def dashboard():
    if not admin_required():
        flash('Admin access only.', 'danger')
        return redirect(url_for('auth.login'))

    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='Trekker').count()
    total_staff = User.query.filter_by(role='Staff').count()
    total_bookings = Booking.query.count()

    return render_template('admin/dashboard.html',
                           total_treks=total_treks,
                           total_users=total_users,
                           total_staff=total_staff,
                           total_bookings=total_bookings)


# ─── Trek Management ──────────────────────────────────────────────────────────

@admin_bp.route('/treks')
def treks():
    if not admin_required():
        return redirect(url_for('auth.login'))

    search = request.args.get('search', '').strip()
    query = Trek.query
    if search:
        if search.isdigit():
            query = query.filter(
                (Trek.id == int(search)) |
                Trek.name.ilike(f'%{search}%') |
                Trek.location.ilike(f'%{search}%')
            )
        else:
            query = query.filter(
                Trek.name.ilike(f'%{search}%') |
                Trek.location.ilike(f'%{search}%')
            )
    all_treks = query.all()
    return render_template('admin/treks.html', treks=all_treks, search=search)


@admin_bp.route('/treks/add', methods=['GET', 'POST'])
def add_trek():
    if not admin_required():
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        try:
            trek = Trek(
                name=request.form['name'],
                location=request.form['location'],
                difficulty=request.form['difficulty'],
                duration_days=int(request.form['duration_days']),
                available_slots=int(request.form['available_slots']),
                status=request.form.get('status', 'Pending'),
                start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d'),
                end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d'),
            )
            db.session.add(trek)
            db.session.commit()
            flash('Trek added successfully!', 'success')
            return redirect(url_for('admin.treks'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding trek: {e}', 'danger')

    return render_template('admin/trek_form.html', trek=None, action='Add')


@admin_bp.route('/treks/<int:trek_id>/edit', methods=['GET', 'POST'])
def edit_trek(trek_id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    trek = Trek.query.get_or_404(trek_id)

    if request.method == 'POST':
        try:
            trek.name = request.form['name']
            trek.location = request.form['location']
            trek.difficulty = request.form['difficulty']
            trek.duration_days = int(request.form['duration_days'])
            trek.available_slots = int(request.form['available_slots'])
            trek.status = request.form['status']
            trek.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
            trek.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
            db.session.commit()
            flash('Trek updated successfully!', 'success')
            return redirect(url_for('admin.treks'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating trek: {e}', 'danger')

    return render_template('admin/trek_form.html', trek=trek, action='Edit')


@admin_bp.route('/treks/<int:trek_id>/delete', methods=['POST'])
def delete_trek(trek_id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    trek = Trek.query.get_or_404(trek_id)
    # Remove bookings first to avoid FK constraint issue
    Booking.query.filter_by(trek_id=trek_id).delete()
    db.session.delete(trek)
    db.session.commit()
    flash('Trek deleted.', 'success')
    return redirect(url_for('admin.treks'))


# ─── Assign Staff to Trek ────────────────────────────────────────────────────

@admin_bp.route('/treks/<int:trek_id>/assign-staff', methods=['GET', 'POST'])
def assign_staff(trek_id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    trek = Trek.query.get_or_404(trek_id)
    approved_staff = (
        User.query
        .join(StaffProfile, User.id == StaffProfile.user_id)
        .filter(User.role == 'Staff', StaffProfile.status == 'Approved', User.is_active_user == True)
        .all()
    )

    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        trek.assigned_staff_id = int(staff_id) if staff_id else None
        db.session.commit()
        flash('Staff assigned to trek.', 'success')
        return redirect(url_for('admin.treks'))

    return render_template('admin/assign_staff.html', trek=trek, staff_list=approved_staff)


# ─── Staff Management ─────────────────────────────────────────────────────────

@admin_bp.route('/staff')
def staff():
    if not admin_required():
        return redirect(url_for('auth.login'))

    search = request.args.get('search', '').strip()
    query = User.query.filter_by(role='Staff')
    if search:
        if search.isdigit():
            query = query.filter(
                (User.id == int(search)) |
                User.username.ilike(f'%{search}%') |
                User.email.ilike(f'%{search}%')
            )
        else:
            query = query.filter(
                User.username.ilike(f'%{search}%') |
                User.email.ilike(f'%{search}%')
            )
    all_staff = query.all()
    return render_template('admin/staff.html', staff_list=all_staff, search=search)


@admin_bp.route('/staff/<int:user_id>/approve', methods=['POST'])
def approve_staff(user_id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    profile = StaffProfile.query.filter_by(user_id=user_id).first_or_404()
    profile.status = 'Approved'
    db.session.commit()
    flash('Staff approved.', 'success')
    return redirect(url_for('admin.staff'))


@admin_bp.route('/staff/<int:user_id>/blacklist', methods=['POST'])
def blacklist_staff(user_id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    user.is_active_user = False
    db.session.commit()
    flash(f'Staff {user.username} has been blacklisted.', 'warning')
    return redirect(url_for('admin.staff'))


@admin_bp.route('/staff/<int:user_id>/activate', methods=['POST'])
def activate_staff(user_id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    user.is_active_user = True
    db.session.commit()
    flash(f'Staff {user.username} has been activated.', 'success')
    return redirect(url_for('admin.staff'))


@admin_bp.route('/staff/<int:user_id>/delete', methods=['POST'])
def delete_staff(user_id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    if user.role != 'Staff':
        flash('Invalid operation.', 'danger')
        return redirect(url_for('admin.staff'))

    # Remove assigned treks
    Trek.query.filter_by(assigned_staff_id=user_id).update({'assigned_staff_id': None})
    # Remove staff profile
    StaffProfile.query.filter_by(user_id=user_id).delete()
    # Remove the user
    db.session.delete(user)
    db.session.commit()
    flash(f'Staff {user.username} has been removed.', 'success')
    return redirect(url_for('admin.staff'))


# ─── User Management ─────────────────────────────────────────────────────────

@admin_bp.route('/users')
def users():
    if not admin_required():
        return redirect(url_for('auth.login'))

    search = request.args.get('search', '').strip()
    query = User.query.filter_by(role='Trekker')
    if search:
        if search.isdigit():
            query = query.filter(
                (User.id == int(search)) |
                User.username.ilike(f'%{search}%') |
                User.email.ilike(f'%{search}%')
            )
        else:
            query = query.filter(
                User.username.ilike(f'%{search}%') |
                User.email.ilike(f'%{search}%')
            )
    all_users = query.all()
    return render_template('admin/users.html', users=all_users, search=search)


@admin_bp.route('/users/<int:user_id>/blacklist', methods=['POST'])
def blacklist_user(user_id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    user.is_active_user = False
    db.session.commit()
    flash(f'User {user.username} has been blacklisted.', 'warning')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/activate', methods=['POST'])
def activate_user(user_id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    user.is_active_user = True
    db.session.commit()
    flash(f'User {user.username} has been activated.', 'success')
    return redirect(url_for('admin.users'))


# ─── Bookings View ────────────────────────────────────────────────────────────

@admin_bp.route('/bookings')
def bookings():
    if not admin_required():
        return redirect(url_for('auth.login'))

    all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=all_bookings)


# ─── Approve Trek ──────────────────────────────────────────────────────────────

@admin_bp.route('/treks/<int:trek_id>/approve', methods=['POST'])
def approve_trek(trek_id):
    if not admin_required():
        return redirect(url_for('auth.login'))

    trek = Trek.query.get_or_404(trek_id)
    if trek.status == 'Pending':
        trek.status = 'Open'
        db.session.commit()
        flash(f'Trek "{trek.name}" is now open for booking.', 'success')
    else:
        flash('Only Pending treks can be approved.', 'warning')
    return redirect(url_for('admin.treks'))


# ─── Trekking History ─────────────────────────────────────────────────────────

@admin_bp.route('/history')
def history():
    if not admin_required():
        return redirect(url_for('auth.login'))

    all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()

    # Deduplicate — keep only the most recent booking per user+trek pair
    seen = set()
    unique_bookings = []
    for b in all_bookings:
        key = (b.user_id, b.trek_id)
        if key not in seen:
            seen.add(key)
            unique_bookings.append(b)

    return render_template('admin/history.html', bookings=unique_bookings)
