from flask import Blueprint, render_template, request

from app.models import Shipment

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
