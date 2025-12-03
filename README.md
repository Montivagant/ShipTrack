# Online Shipment Tracking System

A simple Flask + SQLite web app for managing customers, couriers, shipments, and public tracking.

## Prerequisites
- Python 3.x installed
- (Recommended) `venv` for isolation

## Setup
1) Clone or download the project.
2) Create and activate a virtual environment:
   - Windows: `python -m venv .venv && .venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
3) Install dependencies: `pip install -r requirements.txt`

## Configuration
- Default SQLite database path: `instance/shipment_tracking.db`
- Secret key: set `SECRET_KEY` env var for production (defaults to placeholder in `config.py`).

## Initialize the database
- Using script: `python init_db.py`
- Or Flask CLI: `flask --app run.py init-db`

## Seed sample data
- Command: `python seed_data.py`
- Default credentials after seeding:
  - Admin: `admin@example.com` / `admin123`
  - Couriers (all): `courier123` (emails: `bob.courier@example.com`, `carol.courier@example.com`, `dan.courier@example.com`)

## Run the app
- Start server: `python run.py`
- Default URL: http://127.0.0.1:5000/
- Support form (extra): http://127.0.0.1:5000/support/new

## Project structure
- `app/` Flask app, routes, models, templates, static assets
- `config.py` Configuration (SQLite URI, secret key)
- `run.py` App entrypoint
- `init_db.py` Database initialization helper
- `seed_data.py` Seed script
- `docs/` Architecture, API, and user manual

## Notes
- Stack: Flask, SQLAlchemy, SQLite, Jinja2 templates, Bootstrap 5 via CDN, bcrypt for passwords.
- Extra: lightweight support tickets (public submit, admin respond) and proof links on tracking events.
- Keep `SECRET_KEY` and passwords secure in production.

## Manual test checklist (happy path)
- Admin login works; invalid password shows an error.
- Create/update/delete customer; duplicate email shows warning.
- Create/update/delete courier; duplicate email shows warning; temporary password shown on creation.
- Create shipment with/without courier; invalid date rejected; tracking number auto-generated.
- Edit shipment and assign courier; new "Assigned" event appears.
- Courier login; sees only assigned shipments; can add tracking event (with proof link) and see it appear.
- Public tracking page finds shipment by tracking number and shows timeline; unknown tracking shows friendly message.
