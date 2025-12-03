import secrets
import string
from datetime import datetime

import csv
import io

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from sqlalchemy import func

from app import db
from app.auth_utils import hash_password, login_required
from app.models import Courier, Customer, Shipment, TrackingEvent

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def generate_tracking_number():
    prefix = "TRK"
    while True:
        suffix = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        tracking = f"{prefix}-{suffix}"
        if not Shipment.query.filter_by(tracking_number=tracking).first():
            return tracking


def _validate_required(form_data, required_fields):
    missing = [label for field, label in required_fields if not form_data.get(field)]
    if missing:
        flash(f"Missing required fields: {', '.join(missing)}.", "warning")
        return False
    return True


@admin_bp.route("/dashboard")
@login_required(role="admin")
def dashboard():
    shipments = Shipment.query.all()
    status_counts = {}
    for shipment in shipments:
        status = shipment.latest_status()
        status_counts[status] = status_counts.get(status, 0) + 1

    metrics = {
        "total_shipments": len(shipments),
        "couriers": Courier.query.count(),
        "customers": Customer.query.count(),
        "status_counts": status_counts,
    }
    return render_template("admin/dashboard.html", metrics=metrics)


# Customer Management
@admin_bp.route("/customers")
@login_required(role="admin")
def customers():
    records = Customer.query.order_by(Customer.created_at.desc()).all()
    return render_template("admin/customers_list.html", customers=records)


@admin_bp.route("/customers/new")
@login_required(role="admin")
def new_customer():
    return render_template("admin/customer_form.html", customer=None)


@admin_bp.route("/customers", methods=["POST"])
@login_required(role="admin")
def create_customer():
    data = request.form
    if not _validate_required(
        data,
        [
            ("first_name", "First name"),
            ("last_name", "Last name"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("address", "Address"),
            ("city", "City"),
        ],
    ):
        return redirect(url_for("admin.new_customer"))
    email = data.get("email", "").strip().lower()
    if Customer.query.filter_by(email=email).first():
        flash("Email already exists for another customer.", "warning")
        return redirect(url_for("admin.new_customer"))
    customer = Customer(
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        email=email,
        phone=data.get("phone", ""),
        address=data.get("address", ""),
        city=data.get("city", ""),
    )
    db.session.add(customer)
    db.session.commit()
    flash("Customer created.", "success")
    return redirect(url_for("admin.customers"))


@admin_bp.route("/customers/<int:customer_id>/edit")
@login_required(role="admin")
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return render_template("admin/customer_form.html", customer=customer)


@admin_bp.route("/customers/<int:customer_id>/update", methods=["POST"])
@login_required(role="admin")
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    data = request.form
    if not _validate_required(
        data,
        [
            ("first_name", "First name"),
            ("last_name", "Last name"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("address", "Address"),
            ("city", "City"),
        ],
    ):
        return redirect(url_for("admin.edit_customer", customer_id=customer.id))
    email = data.get("email", "").strip().lower()
    if email != customer.email and Customer.query.filter_by(email=email).first():
        flash("Email already exists for another customer.", "warning")
        return redirect(url_for("admin.edit_customer", customer_id=customer.id))
    customer.first_name = data.get("first_name", "")
    customer.last_name = data.get("last_name", "")
    customer.email = email
    customer.phone = data.get("phone", "")
    customer.address = data.get("address", "")
    customer.city = data.get("city", "")
    db.session.commit()
    flash("Customer updated.", "success")
    return redirect(url_for("admin.customers"))


@admin_bp.route("/customers/<int:customer_id>/delete", methods=["POST"])
@login_required(role="admin")
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash("Customer deleted.", "info")
    return redirect(url_for("admin.customers"))


# Courier Management
@admin_bp.route("/couriers")
@login_required(role="admin")
def couriers():
    records = Courier.query.order_by(Courier.created_at.desc()).all()
    return render_template("admin/couriers_list.html", couriers=records)


@admin_bp.route("/couriers/new")
@login_required(role="admin")
def new_courier():
    return render_template("admin/courier_form.html", courier=None)


@admin_bp.route("/couriers", methods=["POST"])
@login_required(role="admin")
def create_courier():
    data = request.form
    if not _validate_required(
        data,
        [
            ("first_name", "First name"),
            ("last_name", "Last name"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("region", "Region"),
        ],
    ):
        return redirect(url_for("admin.new_courier"))
    email = data.get("email", "").strip().lower()
    if Courier.query.filter_by(email=email).first():
        flash("Email already exists for another courier.", "warning")
        return redirect(url_for("admin.new_courier"))
    temp_password = secrets.token_urlsafe(6)
    courier = Courier(
        first_name=data.get("first_name", ""),
        last_name=data.get("last_name", ""),
        email=email,
        phone=data.get("phone", ""),
        region=data.get("region", ""),
        hire_date=datetime.strptime(data.get("hire_date"), "%Y-%m-%d").date()
        if data.get("hire_date")
        else datetime.utcnow().date(),
        password_hash=hash_password(temp_password),
    )
    db.session.add(courier)
    db.session.commit()
    flash(f"Courier created. Temporary password: {temp_password}", "success")
    return redirect(url_for("admin.couriers"))


@admin_bp.route("/couriers/<int:courier_id>/edit")
@login_required(role="admin")
def edit_courier(courier_id):
    courier = Courier.query.get_or_404(courier_id)
    return render_template("admin/courier_form.html", courier=courier)


@admin_bp.route("/couriers/<int:courier_id>/update", methods=["POST"])
@login_required(role="admin")
def update_courier(courier_id):
    courier = Courier.query.get_or_404(courier_id)
    data = request.form
    if not _validate_required(
        data,
        [
            ("first_name", "First name"),
            ("last_name", "Last name"),
            ("email", "Email"),
            ("phone", "Phone"),
            ("region", "Region"),
        ],
    ):
        return redirect(url_for("admin.edit_courier", courier_id=courier.id))
    email = data.get("email", "").strip().lower()
    if email != courier.email and Courier.query.filter_by(email=email).first():
        flash("Email already exists for another courier.", "warning")
        return redirect(url_for("admin.edit_courier", courier_id=courier.id))
    courier.first_name = data.get("first_name", "")
    courier.last_name = data.get("last_name", "")
    courier.email = email
    courier.phone = data.get("phone", "")
    courier.region = data.get("region", "")
    if data.get("hire_date"):
        courier.hire_date = datetime.strptime(data.get("hire_date"), "%Y-%m-%d").date()
    db.session.commit()
    flash("Courier updated.", "success")
    return redirect(url_for("admin.couriers"))


@admin_bp.route("/couriers/<int:courier_id>/delete", methods=["POST"])
@login_required(role="admin")
def delete_courier(courier_id):
    courier = Courier.query.get_or_404(courier_id)
    db.session.delete(courier)
    db.session.commit()
    flash("Courier deleted.", "info")
    return redirect(url_for("admin.couriers"))


# Shipment Management
@admin_bp.route("/shipments")
@login_required(role="admin")
def shipments():
    status_filter = request.args.get("status")
    search = request.args.get("q", "").strip()
    export = request.args.get("export")

    query = Shipment.query.join(Customer)
    if status_filter:
        # filter by latest status in Python (simpler for SQLite)
        shipments = query.order_by(Shipment.created_at.desc()).all()
        shipments = [s for s in shipments if s.latest_status() == status_filter]
    else:
        shipments = query.order_by(Shipment.created_at.desc()).all()

    if search:
        lower = search.lower()
        shipments = [
            s
            for s in shipments
            if lower in s.tracking_number.lower()
            or lower in s.customer.first_name.lower()
            or lower in s.customer.last_name.lower()
        ]

    if export == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Tracking", "Customer", "Courier", "Status", "Requested"])
        for s in shipments:
            writer.writerow(
                [
                    s.tracking_number,
                    f"{s.customer.first_name} {s.customer.last_name}",
                    f"{s.courier.first_name} {s.courier.last_name}" if s.courier else "Unassigned",
                    s.latest_status(),
                    s.requested_date.strftime("%Y-%m-%d"),
                ]
            )
        output.seek(0)
        return Response(
            output.read(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=shipments.csv"},
        )

    return render_template("admin/shipments_list.html", shipments=shipments, status_filter=status_filter, search=search)


@admin_bp.route("/shipments/new")
@login_required(role="admin")
def new_shipment():
    customers = Customer.query.order_by(Customer.first_name).all()
    couriers = Courier.query.order_by(Courier.first_name).all()
    return render_template("admin/shipment_form.html", shipment=None, customers=customers, couriers=couriers)


@admin_bp.route("/shipments", methods=["POST"])
@login_required(role="admin")
def create_shipment():
    data = request.form
    if not _validate_required(
        data,
        [
            ("customer_id", "Customer"),
            ("sender_address", "Sender address"),
            ("receiver_address", "Receiver address"),
        ],
    ):
        return redirect(url_for("admin.new_shipment"))
    try:
        customer_id = int(data.get("customer_id"))
    except (TypeError, ValueError):
        flash("Invalid customer selection.", "warning")
        return redirect(url_for("admin.new_shipment"))
    try:
        requested_date = (
            datetime.fromisoformat(data.get("requested_date"))
            if data.get("requested_date")
            else datetime.utcnow()
        )
    except ValueError:
        flash("Invalid requested date.", "warning")
        return redirect(url_for("admin.new_shipment"))
    assigned_courier_id = data.get("assigned_courier_id")
    assigned_courier_id = int(assigned_courier_id) if assigned_courier_id else None
    shipment = Shipment(
        customer_id=customer_id,
        sender_address=data.get("sender_address", ""),
        receiver_address=data.get("receiver_address", ""),
        city=data.get("city", ""),
        requested_date=requested_date,
        tracking_number=generate_tracking_number(),
        assigned_courier_id=assigned_courier_id,
    )
    db.session.add(shipment)
    db.session.flush()

    created_event = TrackingEvent(
        shipment_id=shipment.id,
        courier_id=assigned_courier_id,
        status="Created",
        location_description=shipment.city or "Unknown",
        notes="Shipment created",
    )
    db.session.add(created_event)

    if assigned_courier_id:
        assignment_event = TrackingEvent(
            shipment_id=shipment.id,
            courier_id=assigned_courier_id,
            status="Assigned",
            location_description="Courier assigned",
            notes="Courier assigned to shipment",
        )
        db.session.add(assignment_event)

    db.session.commit()
    flash("Shipment created.", "success")
    return redirect(url_for("admin.shipments"))


@admin_bp.route("/shipments/<int:shipment_id>")
@login_required(role="admin")
def shipment_detail(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    return render_template("admin/shipment_detail.html", shipment=shipment)


@admin_bp.route("/shipments/<int:shipment_id>/edit")
@login_required(role="admin")
def edit_shipment(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    customers = Customer.query.order_by(Customer.first_name).all()
    couriers = Courier.query.order_by(Courier.first_name).all()
    return render_template(
        "admin/shipment_form.html", shipment=shipment, customers=customers, couriers=couriers
    )


@admin_bp.route("/shipments/<int:shipment_id>/update", methods=["POST"])
@login_required(role="admin")
def update_shipment(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    data = request.form
    if not _validate_required(
        data,
        [
            ("customer_id", "Customer"),
            ("sender_address", "Sender address"),
            ("receiver_address", "Receiver address"),
        ],
    ):
        return redirect(url_for("admin.edit_shipment", shipment_id=shipment.id))
    try:
        shipment.customer_id = int(data.get("customer_id"))
    except (TypeError, ValueError):
        flash("Invalid customer selection.", "warning")
        return redirect(url_for("admin.edit_shipment", shipment_id=shipment.id))
    try:
        if data.get("requested_date"):
            shipment.requested_date = datetime.fromisoformat(data.get("requested_date"))
    except ValueError:
        flash("Invalid requested date.", "warning")
        return redirect(url_for("admin.edit_shipment", shipment_id=shipment.id))
    previous_courier = shipment.assigned_courier_id
    shipment.sender_address = data.get("sender_address", "")
    shipment.receiver_address = data.get("receiver_address", "")
    shipment.city = data.get("city", "")
    assigned_courier_id = data.get("assigned_courier_id")
    shipment.assigned_courier_id = int(assigned_courier_id) if assigned_courier_id else None

    if shipment.assigned_courier_id and shipment.assigned_courier_id != previous_courier:
        assignment_event = TrackingEvent(
            shipment_id=shipment.id,
            courier_id=shipment.assigned_courier_id,
            status="Assigned",
            location_description="Courier assigned",
            notes="Courier assigned to shipment",
        )
        db.session.add(assignment_event)

    db.session.commit()
    flash("Shipment updated.", "success")
    return redirect(url_for("admin.shipments"))


@admin_bp.route("/shipments/<int:shipment_id>/delete", methods=["POST"])
@login_required(role="admin")
def delete_shipment(shipment_id):
    shipment = Shipment.query.get_or_404(shipment_id)
    db.session.delete(shipment)
    db.session.commit()
    flash("Shipment deleted.", "info")
    return redirect(url_for("admin.shipments"))


@admin_bp.route("/reports")
@login_required(role="admin")
def reports():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    courier_id = request.args.get("courier_id", type=int)
    status_filter = request.args.get("status")

    query = Shipment.query
    if start_date:
        query = query.filter(Shipment.requested_date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(Shipment.requested_date <= datetime.fromisoformat(end_date))
    if courier_id:
        query = query.filter(Shipment.assigned_courier_id == courier_id)
    shipments = query.all()

    filtered_shipments = []
    for shipment in shipments:
        latest_status = shipment.latest_status()
        if status_filter and latest_status != status_filter:
            continue
        filtered_shipments.append({"shipment": shipment, "latest_status": latest_status})

    shipments_per_day = (
        db.session.query(func.date(Shipment.requested_date), func.count(Shipment.id))
        .group_by(func.date(Shipment.requested_date))
        .order_by(func.date(Shipment.requested_date))
        .all()
    )

    shipments_per_courier = (
        db.session.query(
            Courier.first_name,
            Courier.last_name,
            func.count(Shipment.id),
        )
        .join(Shipment, Shipment.assigned_courier_id == Courier.id, isouter=True)
        .group_by(Courier.id)
        .all()
    )

    delivered_shipments = (
        db.session.query(TrackingEvent.shipment_id)
        .filter(TrackingEvent.status == "Delivered")
        .distinct()
        .count()
    )
    total_shipments = Shipment.query.count()

    couriers = Courier.query.order_by(Courier.first_name).all()

    return render_template(
        "admin/reports.html",
        shipments=filtered_shipments,
        shipments_per_day=shipments_per_day,
        shipments_per_courier=shipments_per_courier,
        delivered_shipments=delivered_shipments,
        total_shipments=total_shipments,
        couriers=couriers,
    )
