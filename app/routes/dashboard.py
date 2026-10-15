"""
app/routes/dashboard.py
Main operations dashboard featuring department KPIs, charts, and recent cases.
"""
from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
from app.db import db
from app.models import Case, Evidence, CaseAssignment, User, PublicCrimeIncident, VOfficerWorkload
from app.services.security_service import filter_cases_for_user

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def root():
    return redirect(url_for("dashboard.index"))


@dashboard_bp.route("/dashboard")
@login_required
def index():
    # Enforce multi-level security clearance and need-to-know on case metrics
    base_cases = filter_cases_for_user(Case.query, current_user)

    # 1. High-level Operational KPIs
    total_cases = base_cases.count()
    open_cases = base_cases.filter(Case.status == "Open").count()
    under_investigation = base_cases.filter(Case.status == "Under Investigation").count()
    pending_review = base_cases.filter(Case.status == "Pending Review").count()
    closed_cases = base_cases.filter(Case.status == "Closed").count()
    cold_cases = base_cases.filter(Case.status == "Cold Case").count()

    accessible_case_ids = base_cases.with_entities(Case.case_id).scalar_subquery()
    total_evidence = Evidence.query.filter(Evidence.case_id.in_(accessible_case_ids)).count()
    active_officers = db.session.query(func.count(func.distinct(CaseAssignment.user_id))).filter_by(is_active=True).scalar() or 0
    public_crimes_count = PublicCrimeIncident.query.count()

    # 2. Case Priority Breakdown
    priority_rows = base_cases.with_entities(Case.priority, func.count(Case.case_id)).group_by(Case.priority).all()
    priority_counts = {p: 0 for p in ["Low", "Medium", "High", "Critical"]}
    for p, count in priority_rows:
        if p in priority_counts:
            priority_counts[p] = count

    # 3. Case Type Breakdown
    type_rows = base_cases.with_entities(Case.case_type, func.count(Case.case_id)).group_by(Case.case_type).all()
    type_labels = [row[0] for row in type_rows]
    type_data = [row[1] for row in type_rows]

    # 4. Status Breakdown for Doughnut Chart
    status_labels = ["Open", "Under Investigation", "Pending Review", "Closed", "Cold Case"]
    status_data = [open_cases, under_investigation, pending_review, closed_cases, cold_cases]

    # 5. Top Active Officer Workloads (from v_officer_workload view)
    try:
        workload_records = VOfficerWorkload.query.filter(VOfficerWorkload.active_cases > 0).order_by(VOfficerWorkload.active_cases.desc()).limit(5).all()
    except Exception:
        workload_records = []

    # 6. Recent Cases Dossiers
    recent_cases = base_cases.order_by(Case.date_reported.desc()).limit(8).all()

    return render_template(
        "dashboard/index.html",
        kpis={
            "total_cases": total_cases,
            "open_cases": open_cases,
            "under_investigation": under_investigation,
            "closed_cases": closed_cases,
            "total_evidence": total_evidence,
            "active_officers": active_officers,
            "public_crimes_count": public_crimes_count
        },
        priority_counts=priority_counts,
        type_labels=type_labels,
        type_data=type_data,
        status_labels=status_labels,
        status_data=status_data,
        workload_records=workload_records,
        recent_cases=recent_cases
    )
