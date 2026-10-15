"""
app/routes/citizen.py
Citizen-facing portal for non-emergency public incident reporting and tracking.
Operates completely isolated from internal police user accounts and classified case records.
"""
import random
import string
from datetime import datetime, date
from functools import wraps
from flask import (
    Blueprint, render_template, redirect, url_for, 
    request, flash, session, g, abort
)
from app.db import db
from app.models import Citizen, CitizenReport

citizen_bp = Blueprint("citizen", __name__, url_prefix="/citizen")


def citizen_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        citizen_id = session.get("citizen_id")
        if not citizen_id:
            flash("Please sign in to access the Citizen Portal.", "warning")
            return redirect(url_for("citizen.login", next=request.url))
        
        citizen = Citizen.query.get(citizen_id)
        if not citizen or not citizen.is_active:
            session.pop("citizen_id", None)
            flash("Your citizen session is invalid or has expired.", "danger")
            return redirect(url_for("citizen.login"))
            
        g.current_citizen = citizen
        return f(*args, **kwargs)
    return decorated_function


def generate_tracking_number() -> str:
    """Generates a collision-resistant tracking number (e.g., CR-2026-94821)."""
    current_year = datetime.utcnow().year
    while True:
        suffix = "".join(random.choices(string.digits, k=5))
        tracking_number = f"CR-{current_year}-{suffix}"
        if not CitizenReport.query.filter_by(tracking_number=tracking_number).first():
            return tracking_number


@citizen_bp.route("/")
def index():
    if session.get("citizen_id"):
        return redirect(url_for("citizen.dashboard"))
    return redirect(url_for("citizen.login"))


@citizen_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("citizen_id"):
        return redirect(url_for("citizen.dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        phone_number = request.form.get("phone_number", "").strip()
        address = request.form.get("address", "").strip()

        errors = []
        if not full_name:
            errors.append("Full name is required.")
        if not email or "@" not in email:
            errors.append("A valid email address is required.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")

        if Citizen.query.filter_by(email=email).first():
            errors.append("An account with that email already exists.")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("citizen/register.html", 
                                   full_name=full_name, email=email, 
                                   phone_number=phone_number, address=address)

        citizen = Citizen(
            email=email,
            full_name=full_name,
            phone_number=phone_number or None,
            address=address or None,
            is_active=True
        )
        citizen.set_password(password)

        db.session.add(citizen)
        db.session.commit()

        flash("Registration successful! You may now sign in to your citizen account.", "success")
        return redirect(url_for("citizen.login"))

    return render_template("citizen/register.html")


@citizen_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("citizen_id"):
        return redirect(url_for("citizen.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        citizen = Citizen.query.filter_by(email=email).first()
        if not citizen or not citizen.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("citizen/login.html", email=email)

        if not citizen.is_active:
            flash("This citizen account has been deactivated. Please contact public support.", "danger")
            return render_template("citizen/login.html", email=email)

        session["citizen_id"] = citizen.citizen_id
        flash(f"Welcome to the Citizen Portal, {citizen.full_name}.", "success")
        next_url = request.args.get("next")
        return redirect(next_url or url_for("citizen.dashboard"))

    return render_template("citizen/login.html")


@citizen_bp.route("/logout")
def logout():
    session.pop("citizen_id", None)
    flash("You have been signed out of the Citizen Portal.", "info")
    return redirect(url_for("citizen.login"))


@citizen_bp.route("/dashboard")
@citizen_login_required
def dashboard():
    citizen = g.current_citizen
    reports = (
        CitizenReport.query
        .filter_by(citizen_id=citizen.citizen_id)
        .order_by(CitizenReport.created_at.desc())
        .all()
    )

    total_count = len(reports)
    under_review_count = sum(1 for r in reports if r.status in ("Submitted", "Under Review", "Information Requested"))
    resolved_count = sum(1 for r in reports if r.status in ("Resolved", "Closed"))

    return render_template(
        "citizen/dashboard.html",
        citizen=citizen,
        reports=reports,
        total_count=total_count,
        under_review_count=under_review_count,
        resolved_count=resolved_count
    )


@citizen_bp.route("/reports/new", methods=["GET", "POST"])
@citizen_login_required
def new_report():
    citizen = g.current_citizen
    categories = [
        "Theft / Shoplifting",
        "Vandalism / Property Damage",
        "Lost Property",
        "Noise Disturbance",
        "Suspicious Vehicle / Activity",
        "Scam / Cyber Fraud Attempt",
        "Minor Traffic Incident",
        "Other Non-Emergency Concern"
    ]

    if request.method == "POST":
        category = request.form.get("category", "").strip()
        incident_date_str = request.form.get("incident_date", "").strip()
        incident_location = request.form.get("incident_location", "").strip()
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()

        errors = []
        if not category:
            errors.append("Please select an incident category.")
        if not incident_date_str:
            errors.append("Incident date is required.")
        else:
            try:
                parsed_date = datetime.strptime(incident_date_str, "%Y-%m-%d").date()
                if parsed_date > date.today():
                    errors.append("Incident date cannot be in the future.")
            except ValueError:
                errors.append("Invalid date format. Please use YYYY-MM-DD.")
                parsed_date = None

        if not incident_location:
            errors.append("Incident location is required.")
        if not title:
            errors.append("Report title is required.")
        if not description or len(description) < 15:
            errors.append("Please provide a descriptive explanation (at least 15 characters).")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("citizen/new_report.html", 
                                   categories=categories, category=category,
                                   incident_date=incident_date_str, 
                                   incident_location=incident_location,
                                   title=title, description=description)

        tracking_num = generate_tracking_number()

        new_submission = CitizenReport(
            tracking_number=tracking_num,
            citizen_id=citizen.citizen_id,
            category=category,
            incident_date=parsed_date,
            incident_location=incident_location,
            title=title,
            description=description,
            status="Submitted",
            public_status_notes="Your demonstration report has been logged and assigned for review. Check back for public status updates.",
            is_demo_submission=True
        )

        db.session.add(new_submission)
        db.session.commit()

        flash(
            f"Your report has been submitted successfully! "
            f"Tracking reference: {tracking_num}",
            "success"
        )
        return redirect(url_for("citizen.report_detail", report_id=new_submission.report_id))

    return render_template("citizen/new_report.html", categories=categories, today=date.today().isoformat())


@citizen_bp.route("/reports/<int:report_id>")
@citizen_login_required
def report_detail(report_id):
    citizen = g.current_citizen
    report = CitizenReport.query.get(report_id)

    # Return 404 to avoid information leakage between citizen accounts
    if not report or report.citizen_id != citizen.citizen_id:
        abort(404)

    return render_template("citizen/report_detail.html", report=report, citizen=citizen)
