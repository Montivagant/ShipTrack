from app import create_app, db  # noqa: E402
from app import models  # noqa: F401, E402


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database initialized at", app.config["SQLALCHEMY_DATABASE_URI"])


if __name__ == "__main__":
    main()
