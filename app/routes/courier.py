from datetime import datetime

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app import db
from app.auth_utils import login_required
from app.models import Courier, Shipment, TrackingEvent

courier_bp = Blueprint("courier", __name__, url_prefix="/courier")


def _get_courier():
    courier = Courier.query.get(g.current_user_id)
    if not courier:
        abort(403)
    return courier


@courier_bp.route("/dashboard")
@login_required(role="courier")
def dashboard():
    courier = _get_courier()
    search = request.args.get("q", "").strip()
    shipments = Shipment.query.filter_by(assigned_courier_id=courier.id).order_by(Shipment.created_at.desc()).all()
    if search:
        lower = search.lower()
        shipments = [s for s in shipments if lower in s.tracking_number.lower() or lower in s.customer.first_name.lower() or lower in s.customer.last_name.lower()]
    return render_template("courier/dashboard.html", courier=courier, shipments=shipments, search=search)


@courier_bp.route("/shipments/<int:shipment_id>")
@login_required(role="courier")
def shipment_detail(shipment_id):
    courier = _get_courier()
    shipment = Shipment.query.filter_by(id=shipment_id, assigned_courier_id=courier.id).first_or_404()
    return render_template("courier/shipment_detail.html", shipment=shipment)


@courier_bp.route("/shipments/<int:shipment_id>/track", methods=["GET", "POST"])
@login_required(role="courier")
def track_shipment(shipment_id):
    courier = _get_courier()
    shipment = Shipment.query.filter_by(id=shipment_id, assigned_courier_id=courier.id).first_or_404()

    if request.method == "POST":
        status = request.form.get("status", "").strip()
        location_description = request.form.get("location_description", "").strip()
        notes = request.form.get("notes", "")
        proof_url = request.form.get("proof_url", "").strip()
        if not status or not location_description:
            flash("Status and location are required.", "warning")
            return redirect(url_for("courier.track_shipment", shipment_id=shipment.id))
        event = TrackingEvent(
            shipment_id=shipment.id,
            courier_id=courier.id,
            status=status,
            location_description=location_description or "Unknown",
            notes=notes,
            proof_url=proof_url or None,
            created_at=datetime.utcnow(),
        )
        db.session.add(event)
        db.session.commit()
        flash("Tracking event recorded.", "success")
        return redirect(url_for("courier.shipment_detail", shipment_id=shipment.id))

    return render_template("courier/tracking_form.html", shipment=shipment)
