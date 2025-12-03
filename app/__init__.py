import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from config import Config

STATUS_COLORS = {
    "Created": "secondary",
    "Assigned": "info",
    "Picked up": "primary",
    "Out for delivery": "warning",
    "Attempted/Rescheduled": "warning",
    "Delivered": "success",
    "Returned to sender": "dark",
    "Failed/Returned": "danger",
}

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.courier import courier_bp
    from app.routes.public import public_bp
    from app.routes.support import support_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(courier_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(support_bp)

    @app.context_processor
    def inject_status_helpers():
        hints = {
            "Created": "Shipment created; awaiting assignment.",
            "Assigned": "Courier assigned; pickup scheduled.",
            "Picked up": "Parcel picked up; heading to destination hub.",
            "Out for delivery": "Courier is delivering today.",
            "Attempted/Rescheduled": "Delivery attempt made; rescheduled with recipient.",
            "Delivered": "Delivered to recipient.",
            "Returned to sender": "Parcel is being returned to sender.",
            "Failed/Returned": "Delivery failed; contact support.",
        }
        return {
            "status_badge": lambda status: STATUS_COLORS.get(status, "secondary"),
            "status_choices": list(STATUS_COLORS.keys()),
            "status_hint": lambda status: hints.get(status, ""),
        }

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("500.html"), 500

    @app.cli.command("init-db")
    def init_db_command():
        """Create database tables."""
        from app import models  # noqa: F401
        from app import models_support  # noqa: F401

        with app.app_context():
            db.create_all()
        print("Database initialized.")

    return app
