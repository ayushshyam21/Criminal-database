"""
app/routes/analytics.py
Public Chicago Crime Analytics & Ingestion Service.
Strictly decoupled from internal fictional investigation records.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from sqlalchemy import func, or_, desc
from app.db import db
from app.models import PublicCrimeIncident, IUCRCode, VPublicIncidentTrends
from app.services.chicago_importer import import_chicago_crimes
from app.routes.auth import admin_required

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/public-crimes")
@login_required
def public_crimes():
    search = request.args.get("q", "").strip()
    year_filter = request.args.get("year", "")
    type_filter = request.args.get("type", "")
    district_filter = request.args.get("district", "")
    arrest_filter = request.args.get("arrest", "")
    page = request.args.get("page", 1, type=int)

    query = PublicCrimeIncident.query

    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                PublicCrimeIncident.case_number.ilike(s),
                PublicCrimeIncident.block.ilike(s),
                PublicCrimeIncident.source_primary_type.ilike(s),
                PublicCrimeIncident.source_description.ilike(s)
            )
        )

    if year_filter and year_filter.isdigit():
        query = query.filter(PublicCrimeIncident.incident_year == int(year_filter))
    if type_filter:
        query = query.filter(PublicCrimeIncident.source_primary_type == type_filter)
    if district_filter:
        query = query.filter(PublicCrimeIncident.district == district_filter)
    if arrest_filter in ("true", "1"):
        query = query.filter(PublicCrimeIncident.arrest_made == True)
    elif arrest_filter in ("false", "0"):
        query = query.filter(PublicCrimeIncident.arrest_made == False)

    pagination = query.order_by(PublicCrimeIncident.incident_date.desc()).paginate(page=page, per_page=20, error_out=False)

    # Distinct filter options
    available_years = [r[0] for r in db.session.query(func.distinct(PublicCrimeIncident.incident_year)).order_by(PublicCrimeIncident.incident_year.desc()).all() if r[0]]
    available_types = [r[0] for r in db.session.query(func.distinct(PublicCrimeIncident.source_primary_type)).order_by(PublicCrimeIncident.source_primary_type).all() if r[0]]
    total_count = PublicCrimeIncident.query.count()

    return render_template(
        "analytics/public_crimes.html",
        incidents=pagination.items,
        pagination=pagination,
        search_query=search,
        selected_year=year_filter,
        selected_type=type_filter,
        selected_district=district_filter,
        selected_arrest=arrest_filter,
        available_years=available_years,
        available_types=available_types,
        total_count=total_count
    )


@analytics_bp.route("/public-crimes/import", methods=["POST"])
@login_required
@admin_required
def trigger_import():
    limit_str = request.form.get("limit", "500")
    try:
        limit = int(limit_str)
    except ValueError:
        limit = 500

    result = import_chicago_crimes(limit=limit)

    if result.get("success"):
        flash(
            f"Ingestion Finished: {result.get('records_inserted', 0)} new records added, "
            f"{result.get('duplicates_skipped', 0)} duplicates skipped. ({result.get('message', '')})",
            "success"
        )
    else:
        flash(f"Public Crime API Ingestion Error: {result.get('error', 'Unknown failure')}", "danger")

    return redirect(url_for("analytics.public_crimes"))


@analytics_bp.route("/analytics/trends")
@login_required
def trends():
    # Query database view: v_public_incident_trends
    trends_records = VPublicIncidentTrends.query.order_by(
        VPublicIncidentTrends.incident_year.desc(),
        VPublicIncidentTrends.total_incidents.desc()
    ).limit(30).all()

    # Aggregate by primary type across all public records
    type_stats = db.session.query(
        PublicCrimeIncident.source_primary_type,
        func.count(PublicCrimeIncident.incident_id).label("total"),
        func.sum(func.cast(PublicCrimeIncident.arrest_made, db.Integer)).label("arrests")
    ).group_by(PublicCrimeIncident.source_primary_type).order_by(desc("total")).limit(10).all()

    chart_types = [r[0] for r in type_stats]
    chart_totals = [r[1] for r in type_stats]
    chart_arrests = [int(r[2] or 0) for r in type_stats]

    return render_template(
        "analytics/trends.html",
        trends_records=trends_records,
        chart_types=chart_types,
        chart_totals=chart_totals,
        chart_arrests=chart_arrests
    )
