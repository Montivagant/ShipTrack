from functools import wraps

import bcrypt
from flask import flash, g, redirect, session, url_for


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def login_required(role=None):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if "user_id" not in session or "role" not in session:
                flash("Please log in to continue.", "warning")
                if role == "courier":
                    return redirect(url_for("auth.courier_login"))
                return redirect(url_for("auth.admin_login"))

            if role and session.get("role") != role:
                flash("You do not have access to that page.", "danger")
                if session.get("role") == "courier":
                    return redirect(url_for("courier.dashboard"))
                return redirect(url_for("admin.dashboard"))

            g.current_user_id = session.get("user_id")
            g.current_role = session.get("role")
            return view(*args, **kwargs)

        return wrapped

    return decorator
