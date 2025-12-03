# Architecture

## Overview
- Monolithic Flask app with blueprints for admin, courier, auth, and public tracking.
- SQLite database via SQLAlchemy ORM.
- Server-rendered HTML with Jinja2 + Bootstrap 5 (CDN).
- Session-based auth for admin and courier roles; passwords hashed with bcrypt.

## App Components
- `app/__init__.py`: app factory, config loading, DB init, blueprint registration, error handlers.
- `app/models.py`: SQLAlchemy models and relationships.
- `app/models_support.py`: support ticket/comment models (extra feature).
- `app/routes/*`: blueprints for admin, courier, public, and auth flows.
- `app/routes/support.py`: support ticket submission/list/detail (extra feature).
- `app/auth_utils.py`: password hashing/verification and `login_required` decorator.
- Templates under `app/templates/` grouped by role; shared layouts in `app/templates/layouts/`.
- `init_db.py`: helper to create tables.
- `seed_data.py`: inserts default admin, couriers, customers, shipments, and tracking events.

## Data Model (textual ERD)
- **Customer**: id (PK), first_name, last_name, email (unique), phone, address, city, created_at, updated_at.
  - Relationships: has many Shipments.
- **Courier**: id (PK), first_name, last_name, email (unique), phone, region, hire_date, password_hash, created_at, updated_at.
  - Relationships: has many Shipments; has many TrackingEvents.
- **Admin**: id (PK), first_name, last_name, email (unique), phone, password_hash, created_at, updated_at.
- **Shipment**: id (PK), customer_id (FK->Customer), sender_address, receiver_address, city, requested_date, tracking_number (unique), assigned_courier_id (FK->Courier, nullable), created_at, updated_at.
  - Relationships: belongs to Customer; optional Courier; has many TrackingEvents (ordered by created_at).
  - Helper: `latest_status()` returns most recent tracking status or "Created".
- **TrackingEvent**: id (PK), shipment_id (FK->Shipment), courier_id (FK->Courier, nullable), status (string enum), location_description, notes, proof_url, created_at.
  - Relationships: belongs to Shipment; optional Courier.
- **SupportTicket** (extra feature): id, name, email, role, tracking_number (optional), subject, description, status, created_at, updated_at.
  - Relationships: has many SupportComments.
- **SupportComment** (extra feature): id, ticket_id (FK->SupportTicket), author, body, created_at.

## Key Flows
- **Admin**
  - Dashboard metrics (counts, status breakdown).
  - CRUD customers and couriers (courier creation auto-generates a temporary password).
  - CRUD shipments; generates unique tracking numbers; adds tracking events for "Created" and initial "Assigned" when applicable.
  - Reports with simple filters (date range, courier, status) and summary tables.
- **Courier**
  - Views assigned shipments and their timelines.
  - Adds tracking events (status, location, notes) for assigned shipments.
- **Public**
  - Track page for status lookup by tracking number with full timeline.
- **Support (extra)**
  - Public ticket submission form for customers/couriers.
  - Admin ticket list and detail with status updates and comments.

## Validation and Error Handling
- Server-side validation on admin forms:
  - Required field checks (names, email, phone, addresses, shipment fields).
  - Duplicate email checks for customers and couriers.
  - Date parsing guard for shipment requested_date; invalid formats rejected with a flash.
- Courier tracking updates validate presence of status and location before saving.
- Role-based access enforced via `login_required(role=...)`.
- Custom 404/500 templates registered in app factory; form errors surfaced via flash messages.

## Assumptions
- Status values are simple strings; no formal enum table.
- Shipment status is derived from the latest tracking event; Shipments start with a "Created" event.
- Temporary courier passwords are shown once via flash; couriers should change them later (not implemented in scope).
- SQLite is sufficient for the project scope; no migrations are used.
- Support ticketing is an optional extra module kept lightweight (no email integration).
