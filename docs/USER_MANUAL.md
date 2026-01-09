# User Manual

## Introduction
Web-based shipment tracking for store/warehouse operations. Roles: Admin (manage data), Courier (update status), Customer (public tracking). An extra lightweight support module lets users submit tickets.

## System Requirements & Setup
- Python 3.x
- Recommended: virtual environment
- Install deps: `pip install -r requirements.txt`
- Initialize DB: `python init_db.py`
- Seed sample data: `python seed_data.py`
- Run server: `python run.py` (open http://127.0.0.1:5000/)
- Default credentials (after seed):
  - Admin: `admin@example.com` / `admin123`
  - Couriers: `bob.courier@example.com`, `carol.courier@example.com`, `dan.courier@example.com` (password `courier123`)

## Admin
- Login: `http://127.0.0.1:5000/login/admin`
- Dashboard shows shipment counts and status breakdown.
- Customers: list, add, edit, delete.
- Couriers: list, add (auto temp password), edit, delete.
- Shipments: list, create (auto tracking #), assign courier, edit, view timeline, delete.
- Reports: filter by date range, courier, status; view shipments per day/courier and delivered vs total.
- Support tickets (extra): browse tickets, update status, add comments.
- Print shipment PDF and delivery receipt (delivered only) from shipment detail.
- Common flow:
  1. Log in as admin and open Dashboard for quick stats.
  2. Use the nav pills to manage customers/couriers/shipments.
  3. When creating a shipment, choose a customer, addresses, and optionally assign a courier; the system generates a tracking number.
  4. Open Reports to filter by date/courier/status and review summaries.
  5. Check Support to respond to tickets and post admin comments.

## Courier
- Login: `http://127.0.0.1:5000/login/courier`
- Dashboard shows assigned shipments.
- Shipment detail: view info and timeline.
- Add tracking event: status, location, notes, and optional proof link.
- Print shipment PDF and delivery receipt (delivered only) from shipment detail.
- Common flow:
  1. Log in as courier to reach the dashboard.
  2. Search or click into a shipment to see details and history.
  3. Click "Add tracking event", select status, fill location, optional notes/proof link, and save.

## Customer/Public
- Track page: `http://127.0.0.1:5000/track`
- Enter tracking number to see current status and full timeline.
- Print shipment PDF and delivery receipt (delivered only) from the tracking result.
- Common flow:
  1. Open the track page.
  2. Enter tracking number and submit.
  3. If found, view shipment info and timeline; if not, use the support link to request help.

## Support (extra feature)
- Public support form: `http://127.0.0.1:5000/support/new` to submit a ticket (add tracking number if available).
- Admin ticket queue: `http://127.0.0.1:5000/support/admin` and `/support/admin/<id>` to review, comment, and update status.
- Common flow:
  1. Customer/courier submits ticket with subject/description (tracking optional).
  2. Admin opens ticket list, filters by status, and reviews details.
  3. Admin adds comments or updates status to keep the requester informed.

## Screens (placeholders)
- Admin: login, dashboard, customers list/form, couriers list/form, shipments list/detail/form, reports, support tickets.
- Courier: login, dashboard, shipment detail, add tracking event with proof link.
- Public: home/track page with results; support form.
- Screenshot placeholders: [Admin Dashboard], [Customers List], [Couriers List], [Shipments Detail], [Reports], [Courier Dashboard], [Courier Tracking Form], [Public Track], [Support Ticket].
