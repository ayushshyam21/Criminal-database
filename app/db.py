"""
app/db.py
Database session management and MySQL session variable injection for triggers.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user
from sqlalchemy import text

db = SQLAlchemy()

def init_db(app):
    """Initializes the database with the Flask application."""
    db.init_app(app)

def inject_session_actor():
    """
    Sets MySQL session variables @app_user_id and @app_username
    so that audit and custody triggers (trg_cases_status_audit,
    trg_evidence_custody_update) automatically record the authenticated user.
    """
    if current_user and current_user.is_authenticated:
        try:
            db.session.execute(
                text("SET @app_user_id = :uid, @app_username = :uname;"),
                {"uid": current_user.user_id, "uname": current_user.username}
            )
        except Exception:
            pass
    else:
        try:
            db.session.execute(text("SET @app_user_id = NULL, @app_username = NULL;"))
        except Exception:
            pass
