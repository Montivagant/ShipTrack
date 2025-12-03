from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.auth_utils import check_password, login_required
from app.models import Admin, Courier

auth_bp = Blueprint("auth", __name__, url_prefix="")


@auth_bp.route("/login/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password(password, admin.password_hash):
            session["user_id"] = admin.id
            session["role"] = "admin"
            flash("Welcome back, admin.", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("auth/admin_login.html")


@auth_bp.route("/login/courier", methods=["GET", "POST"])
def courier_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        courier = Courier.query.filter_by(email=email).first()
        if courier and check_password(password, courier.password_hash):
            session["user_id"] = courier.id
            session["role"] = "courier"
            flash("Logged in successfully.", "success")
            return redirect(url_for("courier.dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("auth/courier_login.html")


@auth_bp.route("/logout")
@login_required()
def logout():
    role = session.get("role")
    session.clear()
    flash("You have been logged out.", "info")
    if role == "courier":
        return redirect(url_for("auth.courier_login"))
    return redirect(url_for("auth.admin_login"))
