import os


class Config:
    """Base configuration for the shipment tracking app."""

    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, "instance", "shipment_tracking.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")


class TestConfig(Config):
    """Configuration for tests (uses in-memory SQLite)."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
