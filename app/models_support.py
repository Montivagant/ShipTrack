from datetime import datetime

from app import db


class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # customer or courier
    tracking_number = db.Column(db.String(64))
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Open")
    admin_notes = db.Column(db.Text)
    comments = db.relationship("SupportComment", back_populates="ticket", cascade="all, delete-orphan")


class SupportComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey("support_ticket.id"), nullable=False)
    author = db.Column(db.String(120), nullable=False)  # Admin name/email placeholder
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket = db.relationship("SupportTicket", back_populates="comments")
