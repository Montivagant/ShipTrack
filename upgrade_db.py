"""
Lightweight upgrade helper for SQLite: adds new columns/tables without migrations.
"""
import sqlite3
from pathlib import Path

from app import create_app, db
from app import models_support  # noqa: F401


def ensure_column(conn, table, column, ddl):
    cur = conn.execute(f"PRAGMA table_info({table});")
    cols = [row[1] for row in cur.fetchall()]
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl};")
        print(f"Added column {column} to {table}.")
    else:
        print(f"Column {column} already exists on {table}.")


def main():
    app = create_app()
    db_path = Path(app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", ""))
    conn = sqlite3.connect(db_path)
    ensure_column(conn, "tracking_event", "proof_url", "TEXT")
    conn.commit()
    conn.close()

    with app.app_context():
        db.create_all()
        print("Ensured support ticket tables exist.")
    print("Upgrade complete.")


if __name__ == "__main__":
    main()
