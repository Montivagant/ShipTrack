from io import BytesIO

from flask import Blueprint, abort, render_template, request, send_file

from app.models import Shipment
from app.print_utils import build_receipt_pdf, build_shipment_pdf, find_latest_delivered_event

public_bp = Blueprint("public", __name__)


@public_bp.route("/")
def home():
    return render_template("public/home.html")


@public_bp.route("/track", methods=["GET", "POST"])
def track():
    tracking_number = ""
    shipment = None
    if request.method == "POST":
        tracking_number = request.form.get("tracking_number", "").strip()
    else:
        tracking_number = request.args.get("tracking_number", "").strip()

    if tracking_number:
        shipment = Shipment.query.filter_by(tracking_number=tracking_number).first()

    return render_template("public/track.html", shipment=shipment, tracking_number=tracking_number)


@public_bp.route("/track/print")
def print_shipment():
    tracking_number = request.args.get("tracking_number", "").strip()
    if not tracking_number:
        abort(404)
    shipment = Shipment.query.filter_by(tracking_number=tracking_number).first_or_404()
    pdf_bytes = build_shipment_pdf(shipment)
    filename = f"{shipment.tracking_number}.pdf"
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=filename,
    )


@public_bp.route("/track/receipt")
def print_receipt():
    tracking_number = request.args.get("tracking_number", "").strip()
    if not tracking_number:
        abort(404)
    shipment = Shipment.query.filter_by(tracking_number=tracking_number).first_or_404()
    if shipment.latest_status() != "Delivered":
        abort(404)
    delivered_event = find_latest_delivered_event(shipment)
    if not delivered_event:
        abort(404)
    pdf_bytes = build_receipt_pdf(shipment, delivered_event)
    filename = f"{shipment.tracking_number}-receipt.pdf"
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=filename,
    )
