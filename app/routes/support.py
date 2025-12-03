from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.auth_utils import login_required
from app.models_support import SupportComment, SupportTicket

support_bp = Blueprint("support", __name__, url_prefix="/support")


@support_bp.route("/new", methods=["GET", "POST"])
def new_ticket():
    if request.method == "POST":
        data = request.form
        required = ["name", "email", "role", "subject", "description"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            flash("Please fill in all required fields.", "warning")
            return redirect(url_for("support.new_ticket"))

        ticket = SupportTicket(
            name=data.get("name"),
            email=data.get("email"),
            role=data.get("role"),
            tracking_number=data.get("tracking_number", "").strip(),
            subject=data.get("subject"),
            description=data.get("description"),
            status="Open",
        )
        db.session.add(ticket)
        db.session.commit()
        flash("Your ticket has been submitted. We'll get back to you.", "success")
        return redirect(url_for("public.track"))

    return render_template("support/new_ticket.html")


@support_bp.route("/admin")
@login_required(role="admin")
def admin_tickets():
    status = request.args.get("status")
    query = SupportTicket.query.order_by(SupportTicket.updated_at.desc())
    if status:
        query = query.filter_by(status=status)
    tickets = query.all()
    return render_template("support/admin_tickets.html", tickets=tickets)


@support_bp.route("/admin/<int:ticket_id>", methods=["GET", "POST"])
@login_required(role="admin")
def admin_ticket_detail(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    if request.method == "POST":
        action = request.form.get("action")
        if action == "comment":
            body = request.form.get("comment")
            if body:
                comment = SupportComment(ticket_id=ticket.id, author="Admin", body=body)
                db.session.add(comment)
        if action == "status":
            new_status = request.form.get("status")
            if new_status:
                ticket.status = new_status
        db.session.commit()
        flash("Ticket updated.", "success")
        return redirect(url_for("support.admin_ticket_detail", ticket_id=ticket.id))

    statuses = ["Open", "In Progress", "Resolved", "Closed"]
    return render_template("support/admin_ticket_detail.html", ticket=ticket, statuses=statuses)
