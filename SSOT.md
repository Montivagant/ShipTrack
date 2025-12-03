# Shipment Tracking System – Codex Agent Master Specification

> This file is the **single source of truth** for the implementation of the  
> “Online Shipment Tracking System for Stores and Warehouses”.
>
> As the AI Codex Agent, you MUST follow this spec exactly, without adding extra features
> or changing the scope. Keep things **simple, clean, and well-documented**.

---

## 0. Role & Mindset (For the AI Coding Agent)

1. You are an **AI software engineer** implementing a small but complete web system.
2. Your goals:
   - Implement the system **end-to-end**, from backend to UI to database.
   - Keep the UI **clean, usable, and visually pleasant**, but not over-complicated.
   - Stay **strictly within the described project scope**:
     - Online shipment tracking system.
     - Users: Admin, Courier, Public Customer (tracking only).
   - Avoid:
     - Extra features not mentioned here.
     - Overly complex architecture (no microservices, no message queues, no advanced cloud setups).
3. If something is not fully specified:
   - Make a **simple, reasonable assumption**.
   - **Document** that assumption in `docs/ARCHITECTURE.md`.
   - Do NOT stop or wait for clarifications.

---

## 1. Tech Stack & Environment

> The original course/project document does not mandate a specific programming stack,  
> so you MUST use a simple, portable stack that can run almost anywhere.

You MUST use the following stack:

- **Language:** Python 3.x
- **Web Framework:** Flask
- **Database:** SQLite (single file DB)
- **ORM / DB Layer:** SQLAlchemy (preferred)
- **Templating:** Flask’s built-in Jinja2 templates
- **UI / Styling:** Bootstrap 5 via CDN (NO React/Vue/SPA)
- **Auth:**
  - Cookie-based **session auth** via Flask sessions.
  - Passwords stored as secure hashes (bcrypt or equivalent).

### 1.1 Environment Setup – Instructions for You (Codex)

When you reach the initial setup phase, you MUST:

1. Create a Python virtual environment (or describe how to do it in `README.md`).
2. Create `requirements.txt` including at least:
   - `Flask`
   - `SQLAlchemy`
   - `Flask_SQLAlchemy` (if you choose to use it)
   - `bcrypt` or `passlib[bcrypt]`
   - `python-dotenv` (optional)
3. Write clear **installation and run instructions** in `README.md`:
   - How to create venv.
   - How to install dependencies: `pip install -r requirements.txt`.
   - How to start the app: e.g., `python run.py`.

You MUST explicitly document all environment steps in `README.md` so a non-expert can run the system.

---

## 2. Project Overview (Domain)

### 2.1 Goal

Implement a web-based system to manage and track delivery shipments between stores/warehouses and their customers.

### 2.2 User Roles

You MUST support exactly these roles:

1. **Administrator (Admin)**
   - Logs into an admin panel.
   - Manages Customers (CRUD).
   - Manages Couriers (CRUD).
   - Manages Shipments (CRUD + assigning couriers).
   - Views simple Reports.

2. **Courier**
   - Logs into a courier dashboard.
   - Views shipments assigned to them.
   - Updates the status of shipments via tracking events.

3. **Customer / Public User**
   - Does **not** log in.
   - Uses a **tracking number** to see shipment status and history on a public page.

### 2.3 Core Entities

You MUST implement these entities:

- `Customer`
- `Courier`
- `Admin`
- `Shipment`
- `TrackingEvent`

Do NOT introduce additional core entities unless absolutely necessary, and document any addition.

---

## 3. Project Structure

Create a simple, conventional Flask project structure:

- `app/`
  - `__init__.py` (Flask app factory, DB setup)
  - `models.py` (SQLAlchemy models)
  - `routes/`
    - `admin.py` (admin routes)
    - `courier.py` (courier routes)
    - `public.py` (public tracking routes)
    - `auth.py` (login/logout)
  - `templates/`
    - `layouts/`
      - `base.html`
      - `admin_base.html`
      - `courier_base.html`
    - `admin/`
    - `courier/`
    - `public/`
    - `auth/`
  - `static/`
    - `css/`
    - `js/`
    - `img/`
- `instance/` (optional, for SQLite DB file if using Flask instance folder)
- `docs/`
  - `ARCHITECTURE.md`
  - `API.md`
  - `USER_MANUAL.md`
- `requirements.txt`
- `config.py`
- `run.py` (or `wsgi.py`)
- `README.md`

Keep structure simple and logical.

---

## 4. Database Setup & Configuration

### 4.1 Database Choice

- Use **SQLite** as the database engine.
- Database file name should be something like: `shipment_tracking.db`.
- Place it either:
  - in the `instance/` folder (recommended with Flask), OR
  - in project root.  
  In both cases, document the path in `config.py` and `README.md`.

### 4.2 DB Configuration – Instructions for You (Codex)

You MUST:

1. Define a configuration class in `config.py`, e.g. `Config`:
   - `SQLALCHEMY_DATABASE_URI = "sqlite:///shipment_tracking.db"` or instance-based path.
   - `SQLALCHEMY_TRACK_MODIFICATIONS = False`.
   - `SECRET_KEY` (placeholder value; mention that it should be changed in production).
2. In `app/__init__.py`:
   - Create the Flask app.
   - Load `Config`.
   - Initialize SQLAlchemy with the app.

3. Provide a simple **database initialization command**:
   - Option A: create a `flask` CLI command (e.g., `flask init-db`) that calls `db.create_all()`.
   - Option B: create a simple `init_db.py` script that imports the app and calls `db.create_all()`.

4. In `README.md`, you MUST explain:
   - How to initialize the database (exact command to run).
   - That running the init command will create all tables according to the models.

### 4.3 Data Models

Define SQLAlchemy models in `app/models.py`:

1. `Customer`
   - `id` (PK, integer)
   - `first_name` (string)
   - `last_name` (string)
   - `email` (string, unique)
   - `phone` (string)
   - `address` (string)
   - `city` (string)
   - `created_at`, `updated_at` (timestamps)

2. `Courier`
   - `id` (PK)
   - `first_name`
   - `last_name`
   - `email` (unique)
   - `phone`
   - `region` (string)
   - `hire_date` (date)
   - `password_hash` (string)
   - `created_at`, `updated_at`

3. `Admin`
   - `id` (PK)
   - `first_name`
   - `last_name`
   - `email` (unique)
   - `phone`
   - `password_hash` (string)
   - `created_at`, `updated_at`

4. `Shipment`
   - `id` (PK)
   - `customer_id` (FK → `Customer.id`)
   - `sender_address` (string)
   - `receiver_address` (string)
   - `city` (string, optional)
   - `requested_date` (datetime)
   - `tracking_number` (string, unique)
   - `assigned_courier_id` (nullable FK → `Courier.id`)
   - `created_at`, `updated_at`

5. `TrackingEvent`
   - `id` (PK)
   - `shipment_id` (FK → `Shipment.id`)
   - `courier_id` (nullable FK → `Courier.id`)
   - `status` (string or enum: e.g., "Created", "Assigned", "Picked up", "Out for delivery", "Delivered", "Failed/Returned")
   - `location_description` (string)
   - `notes` (text, nullable)
   - `created_at` (timestamp)

You MUST set up relationships using SQLAlchemy `relationship` where useful.

### 4.4 Documenting the DB

In `docs/ARCHITECTURE.md`, you MUST:

- Add a **Data Model** section describing:
  - Each entity (table).
  - Key fields.
  - Relationships.
- This acts as a textual ERD.

---

## 5. System Setup & Run Instructions (for README & Manual)

You MUST create a clear “System Setup” guide for humans inside `README.md` and summarized in `docs/USER_MANUAL.md`.

At minimum, `README.md` MUST contain:

1. **Prerequisites**
   - Python 3.x installed.
   - (Optional) Virtualenv / venv.

2. **Setup Steps**
   - Clone/download the project.
   - Create and activate virtual environment (commands for Windows and Linux/macOS).
   - Install dependencies:
     - `pip install -r requirements.txt`
   - Initialize database:
     - Example command: `python init_db.py` or `flask init-db`
   - (Optional) Run seed script:
     - Example command: `python seed_data.py`.

3. **Run the System**
   - Exact command to start the server:
     - e.g.: `python run.py` OR `flask run`
   - Default URL to open in the browser:
     - e.g.: `http://127.0.0.1:5000/`

4. **Default Credentials**
   - Example:
     - Admin: email/password
     - Courier: email/password  
   (These must match whatever you seed into the DB.)

You MUST also include a summarized version of these steps under a “System Requirements & Setup” section in `docs/USER_MANUAL.md`.

---

## 6. Implementation Phases – TODO List

You MUST follow these phases in order. After each phase, you MUST update the relevant docs.

### Phase 0 – Project Bootstrap

**TODO:**

- [ ] Initialize a new Git repository.
- [ ] Create Python virtual environment (and document exact commands).
- [ ] Create `requirements.txt` and install dependencies.
- [ ] Create the directory structure described above.
- [ ] Implement `app/__init__.py`:
  - Flask app factory.
  - Config loading.
  - DB initialization (SQLAlchemy).
  - Blueprint registration.
- [ ] Create `run.py` to start the Flask development server.

**Docs:**

- [ ] Create `README.md` with basic setup/run instructions.
- [ ] Create empty `docs/ARCHITECTURE.md`, `docs/API.md`, `docs/USER_MANUAL.md` with section headings.

---

### Phase 1 – Models & Database Initialization

**TODO:**

- [ ] Implement models for `Customer`, `Courier`, `Admin`, `Shipment`, `TrackingEvent` as specified.
- [ ] Set up relationships.
- [ ] Implement DB initialization routine:
  - `db.create_all()` wrapped in a CLI command or script.
- [ ] Implement a simple seed function and script to create:
  - 1 admin user.
  - 2–3 couriers.
  - Several customers.
  - Several shipments and tracking events.

**Docs:**

- [ ] Update `docs/ARCHITECTURE.md` with data model description.
- [ ] Update `README.md` with exact DB init and seed commands.

---

### Phase 2 – Authentication & Authorization

**TODO:**

- [ ] Implement `auth` blueprint:
  - `GET /login/admin`, `POST /login/admin`
  - `GET /login/courier`, `POST /login/courier`
  - `GET /logout`
- [ ] Use sessions to store `user_id` and `role`.
- [ ] Implement password hashing with bcrypt.
- [ ] Implement helpers/decorators:
  - `login_required(role=None)`
- [ ] Create simple login templates in `templates/auth/`.

**Docs:**

- [ ] `docs/API.md`: auth endpoints and behavior.
- [ ] `docs/USER_MANUAL.md`: “Admin Login” & “Courier Login”.

---

### Phase 3 – Admin Layout & Dashboard

**TODO:**

- [ ] Create layout templates:
  - `layouts/base.html`
  - `layouts/admin_base.html`
- [ ] Implement `admin` blueprint route:
  - `GET /admin/dashboard` (admin-only).
- [ ] Show simple metrics on dashboard:
  - Total shipments.
  - Shipments count by current status.
  - Number of couriers.

**Docs:**

- [ ] `docs/USER_MANUAL.md`: “Admin Dashboard” section.

---

### Phase 4 – Admin: Customers Management (CRUD)

**TODO:**

- [ ] Routes:
  - `GET /admin/customers`
  - `GET /admin/customers/new`
  - `POST /admin/customers`
  - `GET /admin/customers/<int:id>/edit`
  - `POST /admin/customers/<int:id>/update`
  - `POST /admin/customers/<int:id>/delete`
- [ ] Templates:
  - `admin/customers_list.html`
  - `admin/customer_form.html`
- [ ] Validation & error handling.

**Docs:**

- [ ] `docs/API.md`: Admin–Customers.
- [ ] `docs/USER_MANUAL.md`: “Managing Customers”.

---

### Phase 5 – Admin: Couriers Management (CRUD)

**TODO:**

- [ ] Routes:
  - `GET /admin/couriers`
  - `GET /admin/couriers/new`
  - `POST /admin/couriers`
  - `GET /admin/couriers/<int:id>/edit`
  - `POST /admin/couriers/<int:id>/update`
  - `POST /admin/couriers/<int:id>/delete`
- [ ] Templates:
  - `admin/couriers_list.html`
  - `admin/courier_form.html`
- [ ] Generate temporary passwords for couriers and show them to admin once.

**Docs:**

- [ ] `docs/API.md`: Admin–Couriers.
- [ ] `docs/USER_MANUAL.md`: “Managing Couriers”.

---

### Phase 6 – Admin: Shipments Management (CRUD + Assignment)

**TODO:**

- [ ] Routes:
  - `GET /admin/shipments`
  - `GET /admin/shipments/new`
  - `POST /admin/shipments`
  - `GET /admin/shipments/<int:id>`
  - `GET /admin/shipments/<int:id>/edit`
  - `POST /admin/shipments/<int:id>/update`
  - `POST /admin/shipments/<int:id>/delete` (optional)
- [ ] Generate unique `tracking_number` on shipment creation.
- [ ] Assign courier:
  - Dropdown in form.
  - On first assignment, create a `TrackingEvent` with status `"Assigned"`.
- [ ] Templates:
  - `admin/shipments_list.html`
  - `admin/shipment_form.html`
  - `admin/shipment_detail.html`

**Docs:**

- [ ] `docs/API.md`: Admin–Shipments.
- [ ] `docs/USER_MANUAL.md`: “Managing Shipments” & “Assigning Couriers”.

---

### Phase 7 – Courier Interface: Shipments & Tracking Updates

**TODO:**

- [ ] `courier` blueprint:
  - `GET /courier/dashboard`
  - `GET /courier/shipments/<int:id>`
  - `GET /courier/shipments/<int:id>/track`
  - `POST /courier/shipments/<int:id>/track`
- [ ] Templates:
  - `courier/dashboard.html`
  - `courier/shipment_detail.html`
  - `courier/tracking_form.html`
- [ ] Each tracking event:
  - Linked to shipment and courier.
  - Saves timestamp.

**Docs:**

- [ ] `docs/API.md`: Courier–Shipments & Tracking.
- [ ] `docs/USER_MANUAL.md`: “Courier Dashboard” & “Updating Shipment Status”.

---

### Phase 8 – Public Shipment Tracking (Customer View)

**TODO:**

- [ ] `public` blueprint:
  - `GET /` – home (optional).
  - `GET /track` – show tracking number form.
  - `POST /track` or `GET /track/result` – show shipment status & history.
- [ ] If shipment is found:
  - Show basic info + current status + full tracking timeline.
- [ ] If not found:
  - Show user-friendly error.

**Docs:**

- [ ] `docs/API.md`: Public tracking endpoint.
- [ ] `docs/USER_MANUAL.md`: “Customer Shipment Tracking”.

---

### Phase 9 – Reports (Admin)

**TODO:**

- [ ] Route:
  - `GET /admin/reports`
- [ ] Filters:
  - Date range, courier, status.
- [ ] Simple HTML tables for:
  - Shipments per day.
  - Shipments per courier.
  - Delivered vs total.
- [ ] Optional CSV export for one report.

**Docs:**

- [ ] `docs/USER_MANUAL.md`: “Reports”.

---

### Phase 10 – Validation, Error Handling & UI Polish

**TODO:**

- [ ] Add server-side validation to all forms.
- [ ] Add error handlers and custom `404.html` / `500.html`.
- [ ] Ensure consistent Bootstrap-based layout and responsive design.
- [ ] Avoid unnecessary JS; keep it simple and usable.

**Docs:**

- [ ] `docs/ARCHITECTURE.md`: section on validation and error handling.

---

### Phase 11 – Tests, Seed Data & Checklist

**TODO:**

- [ ] Create seed script to populate initial data.
- [ ] Add basic tests (if feasible) for core flows.
- [ ] In `README.md` or `docs/ARCHITECTURE.md`, add a manual test checklist.

---

### Phase 12 – Documentation & User Manual

You MUST keep docs updated while coding.

**TODO:**

- [ ] `README.md`: full setup & run guide.
- [ ] `docs/ARCHITECTURE.md`: architecture, data model, flows, assumptions.
- [ ] `docs/API.md`: endpoints grouped by role, with examples.
- [ ] `docs/USER_MANUAL.md`:
  - Introduction.
  - System Requirements & Setup (summary).
  - Admin role.
  - Courier role.
  - Customer tracking.
  - Screen-by-screen usage instructions.
  - Screenshot placeholders.

---

## 7. Constraints & Non-Goals

- DO NOT:
  - Implement payments.
  - Integrate external APIs (maps, SMS, email) unless clearly marked as optional.
  - Use SPA frameworks (React/Vue/Angular).
  - Overcomplicate the architecture.

- ALWAYS:
  - Favor **clarity and simplicity**.
  - Keep UI clean, readable, and consistent with Bootstrap.
  - Document everything relevant so that a student can:
    - Run the project.
    - Understand the architecture.
    - Use the system via the User Manual.

---
