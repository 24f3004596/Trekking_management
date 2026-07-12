# Trekking Management Application

A multi-user web application for managing trekking trips, built as a project for the MAD-1 course using Flask and SQLite.

## About

This application allows an admin to create and manage treks, assign staff guides, and oversee bookings. Registered users (trekkers) can browse available treks, book slots, and track their booking history. Staff members can view their assigned treks and manage participant lists.

There are three roles in the system:
- **Admin** -- manages treks, staff, users, and all bookings; can directly create pre-approved staff accounts
- **Staff** -- views assigned treks and participant details (requires admin approval after self-registration, or can be created directly by admin)
- **Trekker** -- browses open treks, books slots, cancels bookings, and views history

Trek status lifecycle: `Pending → Approved → Open → Closed / Completed`

## Tech Stack

- Python 3 / Flask
- SQLite (via SQLAlchemy)
- Jinja2 templates
- Flask-Migrate for database migrations
- Flask-Bcrypt for password hashing
- Vanilla CSS (no external CSS frameworks — `app/static/css/style.css`)

## Project Structure

```
trekking/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py            # Database models (User, Trek, Booking, StaffProfile)
│   ├── extensions.py        # Flask extensions
│   ├── routes/
│   │   ├── auth.py          # Login, registration, logout
│   │   ├── admin.py         # Admin dashboard and management
│   │   ├── staff.py         # Staff views
│   │   └── user.py          # Trekker dashboard, booking, history
│   ├── templates/           # Jinja2 HTML templates
│   └── static/css/          # style.css (single global stylesheet)
├── config.py                # App configuration
├── init_db.py               # Database seeding script
├── app.py                   # Entry point
└── requirements.txt         # Python dependencies
```

## API Specification

Since this is a full-stack Flask application rendering Jinja templates, the following web routes handle requests, serve pages, and process form submissions instead of returning pure JSON.

### General & Authentication Routes (`/`)
- `GET /` - Root endpoint; redirects to login or dashboard.
- `GET/POST /login` - User login endpoint.
- `GET/POST /register` - User registration endpoint.
- `GET /logout` - Terminates user session.

### Admin Routes (`/admin/*`)
- **Dashboard**: `GET /admin/dashboard`, `GET /admin/history`
- **Treks Management**: `GET /admin/treks`, `GET/POST /admin/treks/add`, `GET/POST /admin/treks/<id>/edit`, `POST /admin/treks/<id>/delete`, `POST /admin/treks/<id>/approve`, `POST /admin/treks/<id>/open`, `GET/POST /admin/treks/<id>/assign-staff`
- **Staff Management**: `GET /admin/staff`, `GET/POST /admin/staff/create`, `POST /admin/staff/<id>/approve`, `POST /admin/staff/<id>/blacklist`, `POST /admin/staff/<id>/activate`, `POST /admin/staff/<id>/delete`
- **Users Management**: `GET /admin/users`, `POST /admin/users/<id>/blacklist`, `POST /admin/users/<id>/activate`
- **Bookings Management**: `GET /admin/bookings`

### Staff Routes (`/staff/*`)
- **Dashboard & Profile**: `GET /staff/dashboard`, `GET/POST /staff/profile`
- **Trek Management**: `GET /staff/treks/<id>`, `POST /staff/treks/<id>/update-slots`, `POST /staff/treks/<id>/update-status`, `POST /staff/treks/<id>/update-phase`, `GET /staff/treks/<id>/participants`

### User (Trekker) Routes (`/user/*`)
- **Dashboard & Profile**: `GET /user/dashboard`, `GET/POST /user/profile`
- **Trek Browsing & Booking**: `GET /user/treks`, `POST /user/treks/<id>/book`
- **Bookings & History**: `GET /user/bookings`, `POST /user/bookings/<id>/cancel`, `GET /user/history`

## How to Run

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```
   python init_db.py
   ```

4. Start the development server:
   ```
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in a browser.

## Default Admin Login

After running `init_db.py`, an admin account is created automatically. Check `init_db.py` for the default credentials.

