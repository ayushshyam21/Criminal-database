"""
app/routes/admin.py
Administrative control panel for staff management, security clearance administration,
and personnel account provisioning.
"""
from functools import wraps
from flask import (
    Blueprint, render_template, redirect, url_for, 
    request, flash, abort
)
from flask_login import login_required, current_user
from app.db import db
from app.models import User, PoliceStation
from app.services.security_service import CLEARANCE_RANKS

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login", next=request.url))
        if not current_user.is_admin:
            flash("Access Restricted: Department Administrator clearance required.", "danger")
            return redirect(url_for("dashboard.index"))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route("/staff")
@login_required
@admin_required
def staff_list():
    users = User.query.order_by(User.user_id.asc()).all()
    stations = PoliceStation.query.order_by(PoliceStation.station_name.asc()).all()
    return render_template(
        "admin/staff.html",
        users=users,
        stations=stations,
        clearance_levels=list(CLEARANCE_RANKS.keys())
    )


@admin_bp.route("/staff/<int:user_id>/clearance", methods=["POST"])
@login_required
@admin_required
def update_clearance(user_id):
    target_user = User.query.get_or_404(user_id)
    
    new_clearance = request.form.get("clearance_level", "").strip().upper()
    if new_clearance not in CLEARANCE_RANKS:
        flash("Invalid security clearance level specified.", "danger")
        return redirect(url_for("admin.staff_list"))

    # Optional account activation toggle
    is_active_val = request.form.get("is_active") == "1"
    
    # Prevent self-deactivation of system administrator
    if target_user.user_id == current_user.user_id and not is_active_val:
        flash("You cannot deactivate your own administrative account.", "warning")
        return redirect(url_for("admin.staff_list"))

    old_clearance = target_user.clearance_level
    target_user.clearance_level = new_clearance
    target_user.is_active = is_active_val

    db.session.commit()
    flash(
        f"Updated personnel clearance for {target_user.full_name} ({target_user.badge_number or target_user.username}): "
        f"{old_clearance} -> {new_clearance}. Status: {'Active' if is_active_val else 'Inactive'}.",
        "success"
    )
    return redirect(url_for("admin.staff_list"))
