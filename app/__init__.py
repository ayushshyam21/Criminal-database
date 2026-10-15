"""
app/__init__.py
Flask Application Factory module.
"""
from flask import Flask, render_template
from flask_login import LoginManager
from app.config import Config
from app.db import db, init_db, inject_session_actor
from app.models import User

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please sign in to access the Criminal Case Management System."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    init_db(app)
    login_manager.init_app(app)

    # Injects MySQL session variables on each authenticated request for audit triggers
    @app.before_request
    def set_db_actor():
        inject_session_actor()

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.cases import cases_bp
    from app.routes.persons import persons_bp
    from app.routes.evidence import evidence_bp
    from app.routes.analytics import analytics_bp
    from app.routes.sql_demo import sql_demo_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(cases_bp)
    app.register_blueprint(persons_bp)
    app.register_blueprint(evidence_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(sql_demo_bp)

    # Custom Jinja Filters
    @app.template_filter("format_dt")
    def format_dt(value, fmt="%b %d, %Y %H:%M"):
        if not value:
            return "—"
        return value.strftime(fmt)

    @app.template_filter("badge_status")
    def badge_status(status):
        mapping = {
            "Open": "bg-primary",
            "Under Investigation": "bg-warning text-dark",
            "Pending Review": "bg-info text-dark",
            "Closed": "bg-success",
            "Cold Case": "bg-secondary"
        }
        return mapping.get(status, "bg-light text-dark")

    @app.template_filter("badge_priority")
    def badge_priority(priority):
        mapping = {
            "Low": "bg-secondary",
            "Medium": "bg-info text-dark",
            "High": "bg-warning text-dark",
            "Critical": "bg-danger"
        }
        return mapping.get(priority, "bg-light text-dark")

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template("errors/500.html", error=str(e)), 500

    return app
