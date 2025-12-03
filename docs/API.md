# API / Routes Reference

Server-rendered HTML endpoints grouped by role. All protected routes use the session `role` (`admin` or `courier`) with `login_required`.

## Auth
- `GET /login/admin` / `POST /login/admin` — admin login.
- `GET /login/courier` / `POST /login/courier` — courier login.
- `GET /logout` — clear session.

## Admin
- Dashboard: `GET /admin/dashboard`
- Customers:
  - `GET /admin/customers`
  - `GET /admin/customers/new`
  - `POST /admin/customers`
  - `GET /admin/customers/<id>/edit`
  - `POST /admin/customers/<id>/update`
  - `POST /admin/customers/<id>/delete`
- Couriers:
  - `GET /admin/couriers`
  - `GET /admin/couriers/new`
  - `POST /admin/couriers`
  - `GET /admin/couriers/<id>/edit`
  - `POST /admin/couriers/<id>/update`
  - `POST /admin/couriers/<id>/delete`
- Shipments:
  - `GET /admin/shipments`
  - `GET /admin/shipments/new`
  - `POST /admin/shipments`
  - `GET /admin/shipments/<id>`
  - `GET /admin/shipments/<id>/edit`
  - `POST /admin/shipments/<id>/update`
  - `POST /admin/shipments/<id>/delete`
- Reports:
  - `GET /admin/reports` — filters: `start_date`, `end_date`, `courier_id`, `status`

## Courier
- `GET /courier/dashboard`
- `GET /courier/shipments/<id>`
- `GET /courier/shipments/<id>/track`
- `POST /courier/shipments/<id>/track` (fields: `status`, `location_description`, `notes` optional, `proof_url` optional)

## Public
- `GET /` — landing with track form
- `GET /track` — track form/view
- `POST /track` — lookup by tracking number

## Support (extra feature)
- `GET /support/new` / `POST /support/new` — public ticket submission (fields: name, email, role, tracking_number optional, subject, description).
- `GET /support/admin` — admin-only list of tickets (optional `status` filter).
- `GET /support/admin/<ticket_id>` — admin-only detail; `POST` to add comment or update status.
