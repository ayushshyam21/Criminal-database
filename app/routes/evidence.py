"""
app/routes/evidence.py
Evidence repository management and immutable Chain-of-Custody tracking.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_, text
from app.db import db
from app.models import Evidence, EvidenceCustodyLog, Case

evidence_bp = Blueprint("evidence", __name__, url_prefix="/evidence")


@evidence_bp.route("", strict_slashes=False)
@evidence_bp.route("/", strict_slashes=False)
@login_required
def list_evidence():
    search = request.args.get("q", "").strip()
    type_filter = request.args.get("type", "")
    status_filter = request.args.get("status", "")
    page = request.args.get("page", 1, type=int)

    query = Evidence.query

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                Evidence.evidence_code.ilike(s),
                Evidence.description.ilike(s),
                Evidence.current_storage_location.ilike(s)
            )
        )

    if type_filter:
        query = query.filter(Evidence.evidence_type == type_filter)
    if status_filter:
        query = query.filter(Evidence.current_custody_status == status_filter)

    pagination = query.order_by(Evidence.collected_date.desc()).paginate(page=page, per_page=12, error_out=False)

    return render_template(
        "evidence/list.html",
        evidence_items=pagination.items,
        pagination=pagination,
        search_query=search,
        selected_type=type_filter,
        selected_status=status_filter
    )


@evidence_bp.route("/<int:evidence_id>")
@login_required
def evidence_detail(evidence_id):
    item = Evidence.query.get_or_404(evidence_id)
    custody_history = EvidenceCustodyLog.query.filter_by(
        evidence_id=evidence_id
    ).order_by(EvidenceCustodyLog.logged_at.desc()).all()

    return render_template(
        "evidence/detail.html",
        evidence=item,
        custody_history=custody_history
    )


@evidence_bp.route("/<int:evidence_id>/transfer", methods=["POST"])
@login_required
def transfer_custody(evidence_id):
    """
    Transfers custody location and/or status.
    Note: Updating evidence automatically fires trg_evidence_custody_update,
    which writes an append-only row to evidence_custody_log with handler = @app_user_id!
    """
    item = Evidence.query.get_or_404(evidence_id)
    new_status = request.form.get("new_status")
    new_location = request.form.get("new_location", "").strip()
    reason = request.form.get("reason", "").strip()

    if not new_location:
        flash("Destination storage location is required.", "warning")
        return redirect(url_for("evidence.evidence_detail", evidence_id=evidence_id))
    if not reason:
        flash("A formal reason for transfer must be recorded for chain-of-custody integrity.", "warning")
        return redirect(url_for("evidence.evidence_detail", evidence_id=evidence_id))

    # Set custom transfer reason in MySQL session variable for trigger to capture
    try:
        db.session.execute(
            text("SET @app_transfer_reason = :reason;"),
            {"reason": f"{reason} (Transferred by {current_user.full_name})"}
        )
    except Exception:
        pass

    item.current_custody_status = new_status
    item.current_storage_location = new_location

    try:
        db.session.commit()
        flash(f"Evidence {item.evidence_code} custody transferred. Chain-of-custody logged by trigger.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to transfer custody: {str(e)}", "danger")

    return redirect(url_for("evidence.evidence_detail", evidence_id=evidence_id))
