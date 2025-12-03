from datetime import datetime

from app import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Customer(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(120), nullable=False)

    shipments = db.relationship("Shipment", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer {self.email}>"


class Courier(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(120), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    shipments = db.relationship("Shipment", back_populates="courier")
    tracking_events = db.relationship("TrackingEvent", back_populates="courier")

    def __repr__(self):
        return f"<Courier {self.email}>"


class Admin(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Admin {self.email}>"


class Shipment(db.Model, TimestampMixin):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.id"), nullable=False)
    sender_address = db.Column(db.String(255), nullable=False)
    receiver_address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(120))
    requested_date = db.Column(db.DateTime, nullable=False)
    tracking_number = db.Column(db.String(64), unique=True, nullable=False)
    assigned_courier_id = db.Column(db.Integer, db.ForeignKey("courier.id"))

    customer = db.relationship("Customer", back_populates="shipments")
    courier = db.relationship("Courier", back_populates="shipments")
    tracking_events = db.relationship(
        "TrackingEvent", back_populates="shipment", cascade="all, delete-orphan", order_by="TrackingEvent.created_at"
    )

    def latest_status(self):
        if self.tracking_events:
            return self.tracking_events[-1].status
        return "Created"

    def __repr__(self):
        return f"<Shipment {self.tracking_number}>"


class TrackingEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey("shipment.id"), nullable=False)
    courier_id = db.Column(db.Integer, db.ForeignKey("courier.id"))
    status = db.Column(db.String(50), nullable=False)
    location_description = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text)
    proof_url = db.Column(db.String(512))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    shipment = db.relationship("Shipment", back_populates="tracking_events")
    courier = db.relationship("Courier", back_populates="tracking_events")

    def __repr__(self):
        return f"<TrackingEvent {self.status} for {self.shipment_id}>"
