import random
import string
from datetime import datetime, timedelta

from app import create_app, db
from app.auth_utils import hash_password
from app.models import Admin, Courier, Customer, Shipment, TrackingEvent


def generate_tracking_number():
    prefix = "TRK"
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"{prefix}-{suffix}"


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        if not Admin.query.first():
            admin = Admin(
                first_name="Alice",
                last_name="Admin",
                email="admin@example.com",
                phone="1234567890",
                password_hash=hash_password("admin123"),
            )
            db.session.add(admin)

        courier_data = [
            ("Bob", "Courier", "bob.courier@example.com", "555-1000", "Central"),
            ("Carol", "Courier", "carol.courier@example.com", "555-2000", "East"),
            ("Dan", "Courier", "dan.courier@example.com", "555-3000", "West"),
        ]
        couriers = []
        for first, last, email, phone, region in courier_data:
            courier = Courier.query.filter_by(email=email).first()
            if not courier:
                courier = Courier(
                    first_name=first,
                    last_name=last,
                    email=email,
                    phone=phone,
                    region=region,
                    hire_date=datetime.utcnow().date() - timedelta(days=120),
                    password_hash=hash_password("courier123"),
                )
                db.session.add(courier)
            couriers.append(courier)

        customer_data = [
            ("John", "Doe", "john.doe@example.com", "444-1234", "123 Main St", "Springfield"),
            ("Jane", "Smith", "jane.smith@example.com", "444-5678", "456 Oak Ave", "Shelbyville"),
            ("Mike", "Brown", "mike.brown@example.com", "444-9012", "789 Pine Rd", "Capital City"),
        ]
        customers = []
        for first, last, email, phone, address, city in customer_data:
            customer = Customer.query.filter_by(email=email).first()
            if not customer:
                customer = Customer(
                    first_name=first,
                    last_name=last,
                    email=email,
                    phone=phone,
                    address=address,
                    city=city,
                )
                db.session.add(customer)
            customers.append(customer)

        db.session.commit()

        if not Shipment.query.first():
            for idx, customer in enumerate(customers):
                courier = couriers[idx % len(couriers)]
                shipment = Shipment(
                    customer_id=customer.id,
                    sender_address=customer.address,
                    receiver_address=f"{customer.city} Distribution Center",
                    city=customer.city,
                    requested_date=datetime.utcnow() - timedelta(days=idx),
                    tracking_number=generate_tracking_number(),
                    assigned_courier_id=courier.id,
                )
                db.session.add(shipment)
                db.session.flush()
                events = [
                    TrackingEvent(
                        shipment_id=shipment.id,
                        courier_id=courier.id,
                        status="Created",
                        location_description=customer.city,
                        notes="Shipment created",
                        created_at=shipment.requested_date,
                    ),
                    TrackingEvent(
                        shipment_id=shipment.id,
                        courier_id=courier.id,
                        status="Assigned",
                        location_description=courier.region,
                        notes="Courier assigned",
                        created_at=shipment.requested_date + timedelta(hours=2),
                    ),
                    TrackingEvent(
                        shipment_id=shipment.id,
                        courier_id=courier.id,
                        status="Out for delivery",
                        location_description=courier.region,
                        notes="On the way",
                        created_at=shipment.requested_date + timedelta(hours=6),
                    ),
                ]
                db.session.add_all(events)

        db.session.commit()
        print("Seed data inserted.")


if __name__ == "__main__":
    seed()
