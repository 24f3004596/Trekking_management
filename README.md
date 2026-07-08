# Trekking Management Application

A multi-user web application for managing trekking trips, built as a project for the MAD-1 course using Flask and SQLite.

## About

This application allows an admin to create and manage treks, assign staff guides, and oversee bookings. Registered users (trekkers) can browse available treks, book slots, and track their booking history. Staff members can view their assigned treks and manage participant lists.

There are three roles in the system:
- **Admin** -- manages treks, staff, users, and all bookings
- **Staff** -- views assigned treks and participant details (requires admin approval after registration)
- **Trekker** -- browses open treks, books slots, cancels bookings, and views history

## Tech Stack

- Python 3 / Flask
- SQLite (via SQLAlchemy)
- Jinja2 templates
- Flask-Migrate for database migrations
- Flask-Bcrypt for password hashing
- Vanilla CSS (no Bootstrap)

## Project Structure

```
trekking 2/
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
│   └── static/              # CSS and images
├── config.py                # App configuration
├── init_db.py               # Database seeding script
├── run.py                   # Entry point
└── requirements.txt         # Python dependencies
```

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
   python run.py
   ```

5. Open `http://127.0.0.1:5000` in a browser.

## Default Admin Login

After running `init_db.py`, an admin account is created automatically. Check `init_db.py` for the default credentials.
