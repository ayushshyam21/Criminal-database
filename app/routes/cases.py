"""
app/routes/cases.py
Criminal Case Management CRUD, personnel assignments, person association,
evidence cataloging, and case diary notes.
"""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import text, func, or_
from app.db import db
from app.models import (
    Case, PoliceStation, User, Person, CaseAssignment, 
    CasePerson, Evidence, InvestigationNote, EvidenceCustodyLog
)
from app.routes.auth import admin_required, investigator_or_admin_required
from app.services.security_service import (
    filter_cases_for_user, can_access_case, CLEARANCE_RANKS, get_clearance_rank
)

cases_bp = Blueprint("cases", __name__, url_prefix="/cases")


@cases_bp.route("", strict_slashes=False)
@cases_bp.route("/", strict_slashes=False)
@login_required
def list_cases():
    query_str = request.args.get("q", "").strip()
    status_filter = request.args.get("status", "")
    priority_filter = request.args.get("priority", "")
    type_filter = request.args.get("case_type", "")
    station_filter = request.args.get("station_id", "")
    classification_filter = request.args.get("classification", "")
    page = request.args.get("page", 1, type=int)

    query = Case.query

    if query_str:
        search = f"%{query_str}%"
        query = query.filter(
            or_(
                Case.case_number.ilike(search),
                Case.title.ilike(search),
                Case.incident_location.ilike(search),
                Case.description.ilike(search)
            )
        )

    if status_filter:
        query = query.filter(Case.status == status_filter)
    if priority_filter:
        query = query.filter(Case.priority == priority_filter)
    if type_filter:
        query = query.filter(Case.case_type == type_filter)
    if station_filter and station_filter.isdigit():
        query = query.filter(Case.station_id == int(station_filter))
    if classification_filter:
        query = query.filter(Case.classification_level == classification_filter)

    # Enforce Bell-LaPadula clearance level + Need-to-Know filtering
    query = filter_cases_for_user(query, current_user)

    pagination = query.order_by(Case.date_reported.desc()).paginate(page=page, per_page=12, error_out=False)
    stations = PoliceStation.query.order_by(PoliceStation.station_name).all()

    return render_template(
        "cases/list.html",
        cases=pagination.items,
        pagination=pagination,
        stations=stations,
        clearance_levels=list(CLEARANCE_RANKS.keys()),
        selected_status=status_filter,
        selected_priority=priority_filter,
        selected_type=type_filter,
        selected_station=station_filter,
        selected_classification=classification_filter,
        search_query=query_str
    )


@cases_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_case():
    stations = PoliceStation.query.order_by(PoliceStation.station_name).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        station_id = request.form.get("station_id")
        case_type = request.form.get("case_type")
        priority = request.form.get("priority", "Medium")
        incident_location = request.form.get("incident_location", "").strip()
        description = request.form.get("description", "").strip()

        classification = request.form.get("classification_level", "INTERNAL").strip().upper()
        if classification not in CLEARANCE_RANKS:
            classification = "INTERNAL"

        # Clearance hierarchy: Cannot file a case above own clearance level
        user_clearance = getattr(current_user, "clearance_level", "INTERNAL")
        if get_clearance_rank(classification) > get_clearance_rank(user_clearance):
            flash(f"You cannot create a '{classification}' classified dossier with your current '{user_clearance}' clearance.", "danger")
            return render_template("cases/create.html", stations=stations, clearance_levels=list(CLEARANCE_RANKS.keys()))

        # Validation
        if not title or len(title) < 5:
            flash("Case title must be at least 5 characters long.", "danger")
            return render_template("cases/create.html", stations=stations, clearance_levels=list(CLEARANCE_RANKS.keys()))
        if not station_id or not station_id.isdigit():
            flash("Please select a valid precinct station.", "danger")
            return render_template("cases/create.html", stations=stations, clearance_levels=list(CLEARANCE_RANKS.keys()))
        if not incident_location:
            flash("Incident location is required.", "danger")
            return render_template("cases/create.html", stations=stations, clearance_levels=list(CLEARANCE_RANKS.keys()))

        # Generate unique case number: CASE-YYYY-XXXX
        current_year = datetime.utcnow().year
        last_case = Case.query.filter(Case.case_number.like(f"CASE-{current_year}-%")).order_by(Case.case_id.desc()).first()
        if last_case and last_case.case_number:
            try:
                seq = int(last_case.case_number.split("-")[-1]) + 1
            except ValueError:
                seq = Case.query.count() + 1
        else:
            seq = Case.query.count() + 1
        case_number = f"CASE-{current_year}-{seq:04d}"

        new_case = Case(
            case_number=case_number,
            station_id=int(station_id),
            title=title,
            description=description if description else None,
            case_type=case_type,
            status="Open",
            priority=priority,
            classification_level=classification,
            incident_location=incident_location,
            date_reported=datetime.utcnow(),
            created_by=current_user.user_id,
            is_fictional=True
        )

        try:
            db.session.add(new_case)
            db.session.commit()
            flash(f"Case dossier {case_number} created successfully.", "success")
            return redirect(url_for("cases.case_detail", case_id=new_case.case_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to create case: {str(e)}", "danger")

    return render_template("cases/create.html", stations=stations, clearance_levels=list(CLEARANCE_RANKS.keys()))


@cases_bp.route("/<int:case_id>")
@login_required
def case_detail(case_id):
    case = Case.query.get_or_404(case_id)

    # Enforce Bell-LaPadula clearance level + Need-to-Know authorization
    allowed, reason = can_access_case(current_user, case, action="view")
    if not allowed:
        flash(reason, "danger")
        abort(403, description=reason)

    # 1. Execute Stored Function: fn_case_duration
    try:
        res = db.session.execute(
            text("SELECT fn_case_duration(:cid) AS duration;"),
            {"cid": case_id}
        ).fetchone()
        duration_days = res[0] if res and res[0] is not None else 0
    except Exception:
        duration_days = 0

    # 2. Available personnel for assignment (active officers/investigators)
    available_users = User.query.filter_by(is_active=True).order_by(User.full_name).all()

    # 3. Available fictional persons for case-person linking
    linked_person_ids = [cp.person_id for cp in case.involved_persons]
    available_persons = Person.query.filter(
        ~Person.person_id.in_(linked_person_ids) if linked_person_ids else True
    ).order_by(Person.first_name).all()

    # 4. Filter confidential investigation notes if viewer is not Investigator/Admin
    can_view_confidential = current_user.role in ("Investigator", "Admin")
    visible_notes = [
        n for n in case.notes if not n.is_confidential or can_view_confidential
    ]

    # 5. Fetch custody log timeline for all evidence in this case
    evidence_ids = [e.evidence_id for e in case.evidence_items]
    custody_logs = []
    if evidence_ids:
        custody_logs = EvidenceCustodyLog.query.filter(
            EvidenceCustodyLog.evidence_id.in_(evidence_ids)
        ).order_by(EvidenceCustodyLog.logged_at.desc()).all()

    return render_template(
        "cases/detail.html",
        case=case,
        duration_days=duration_days,
        available_users=available_users,
        available_persons=available_persons,
        visible_notes=visible_notes,
        custody_logs=custody_logs,
        can_view_confidential=can_view_confidential
    )


@cases_bp.route("/<int:case_id>/edit", methods=["GET", "POST"])
@login_required
def edit_case(case_id):
    case = Case.query.get_or_404(case_id)
    stations = PoliceStation.query.order_by(PoliceStation.station_name).all()

    # Enforce authorization to modify case
    allowed, reason = can_access_case(current_user, case, action="edit")
    if not allowed:
        flash(reason, "danger")
        abort(403, description=reason)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        case_type = request.form.get("case_type")
        status = request.form.get("status")
        priority = request.form.get("priority")
        incident_location = request.form.get("incident_location", "").strip()
        description = request.form.get("description", "").strip()
        station_id = request.form.get("station_id")
        classification_val = request.form.get("classification_level")

        if not title:
            flash("Case title cannot be empty.", "danger")
            return render_template("cases/edit.html", case=case, stations=stations, clearance_levels=list(CLEARANCE_RANKS.keys()))

        # If user changed classification level, ensure they hold sufficient clearance
        if classification_val and classification_val.upper() in CLEARANCE_RANKS:
            req_rank = get_clearance_rank(classification_val)
            user_rank = get_clearance_rank(current_user.clearance_level)
            if req_rank <= user_rank:
                case.classification_level = classification_val.upper()
            else:
                flash(f"Cannot escalate dossier to '{classification_val}' beyond your clearance.", "warning")

        case.title = title
        case.case_type = case_type
        case.priority = priority
        case.incident_location = incident_location
        case.description = description if description else None
        if station_id and station_id.isdigit():
            case.station_id = int(station_id)

        # Closure consistency validation (enforces chk_cases_closure_consistency)
        if status == "Closed":
            if case.status != "Closed":
                case.status = "Closed"
                case.date_closed = datetime.utcnow()
        else:
            case.status = status
            case.date_closed = None

        try:
            db.session.commit()
            flash("Case dossier updated successfully.", "success")
            return redirect(url_for("cases.case_detail", case_id=case.case_id))
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to update case: {str(e)}", "danger")

    return render_template("cases/edit.html", case=case, stations=stations, clearance_levels=list(CLEARANCE_RANKS.keys()))


@cases_bp.route("/<int:case_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_case(case_id):
    case = Case.query.get_or_404(case_id)
    allowed, reason = can_access_case(current_user, case, action="delete")
    if not allowed:
        flash(reason, "danger")
        abort(403, description=reason)

    case_number = case.case_number
    try:
        db.session.delete(case)
        db.session.commit()
        flash(f"Case {case_number} deleted successfully.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to delete case: {str(e)}", "danger")
    return redirect(url_for("cases.list_cases"))


@cases_bp.route("/<int:case_id>/assign", methods=["POST"])
@login_required
def assign_personnel(case_id):
    """
    Allocates personnel using the atomic stored procedure sp_assign_case.
    Enforces single active lead investigator and advances status.
    """
    case = Case.query.get_or_404(case_id)
    allowed, reason = can_access_case(current_user, case, action="edit")
    if not allowed:
        flash(reason, "danger")
        abort(403, description=reason)

    user_id = request.form.get("user_id")
    role = request.form.get("role", "Assisting Officer")
    notes = request.form.get("notes", "")

    if not user_id or not user_id.isdigit():
        flash("Please select a certified personnel officer.", "warning")
        return redirect(url_for("cases.case_detail", case_id=case_id))

    try:
        raw_conn = db.session.connection().connection
        with raw_conn.cursor() as cursor:
            cursor.execute(
                "CALL sp_assign_case(%s, %s, %s, %s, @status_code, @status_message);",
                (case_id, int(user_id), role, notes)
            )
            cursor.execute("SELECT @status_code AS code, @status_message AS msg;")
            res = cursor.fetchone()
            
            if isinstance(res, dict):
                code, msg = res["code"], res["msg"]
            else:
                code, msg = res[0], res[1]

        db.session.commit()

        if code == "SUCCESS":
            flash(f"Personnel assignment completed: {msg}", "success")
        else:
            flash(f"Assignment rejected ({code}): {msg}", "danger")

    except Exception as e:
        db.session.rollback()
        flash(f"Database error executing sp_assign_case: {str(e)}", "danger")

    return redirect(url_for("cases.case_detail", case_id=case_id))


@cases_bp.route("/<int:case_id>/unassign/<int:assignment_id>", methods=["POST"])
@login_required
def unassign_personnel(case_id, assignment_id):
    case = Case.query.get_or_404(case_id)
    allowed, reason = can_access_case(current_user, case, action="edit")
    if not allowed:
        flash(reason, "danger")
        abort(403, description=reason)

    assignment = CaseAssignment.query.get_or_404(assignment_id)
    if assignment.case_id != case_id:
        flash("Assignment does not match target case.", "danger")
        return redirect(url_for("cases.case_detail", case_id=case_id))

    assignment.is_active = False
    assignment.unassigned_date = datetime.utcnow()
    assignment.notes = f"{assignment.notes or ''} [Deallocated by {current_user.username}]".strip()

    try:
        db.session.commit()
        flash("Personnel assignment concluded successfully.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to conclude assignment: {str(e)}", "danger")

    return redirect(url_for("cases.case_detail", case_id=case_id))


@cases_bp.route("/<int:case_id>/add-person", methods=["POST"])
@login_required
def add_person(case_id):
    case = Case.query.get_or_404(case_id)
    allowed, reason = can_access_case(current_user, case, action="edit")
    if not allowed:
        flash(reason, "danger")
        abort(403, description=reason)

    person_id = request.form.get("person_id")
    role_in_case = request.form.get("role_in_case")
    statement_summary = request.form.get("statement_summary", "").strip()

    if not person_id or not person_id.isdigit():
        flash("Please select a fictional persona.", "warning")
        return redirect(url_for("cases.case_detail", case_id=case_id))

    case_person = CasePerson(
        case_id=case_id,
        person_id=int(person_id),
        role_in_case=role_in_case,
        statement_summary=statement_summary if statement_summary else None,
        added_at=datetime.utcnow()
    )

    try:
        db.session.add(case_person)
        db.session.commit()
        flash("Persona linked to case successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to associate persona: {str(e)}", "danger")

    return redirect(url_for("cases.case_detail", case_id=case_id))


@cases_bp.route("/<int:case_id>/add-evidence", methods=["POST"])
@login_required
def add_evidence(case_id):
    case = Case.query.get_or_404(case_id)
    allowed, reason = can_access_case(current_user, case, action="edit")
    if not allowed:
        flash(reason, "danger")
        abort(403, description=reason)

    evidence_type = request.form.get("evidence_type")
    description = request.form.get("description", "").strip()
    storage_location = request.form.get("current_storage_location", "").strip()

    if not description or not storage_location:
        flash("Evidence description and storage location are required.", "warning")
        return redirect(url_for("cases.case_detail", case_id=case_id))

    count = Evidence.query.filter_by(case_id=case_id).count() + 1
    evidence_code = f"EVD-{case_id:04d}-{count:03d}"

    evidence = Evidence(
        case_id=case_id,
        evidence_code=evidence_code,
        evidence_type=evidence_type,
        description=description,
        current_storage_location=storage_location,
        current_custody_status="Collected",
        collected_date=datetime.utcnow(),
        collected_by=current_user.user_id,
        created_at=datetime.utcnow()
    )

    try:
        db.session.add(evidence)
        db.session.commit()
        flash(f"Evidence {evidence_code} cataloged. Initial custody logged by trigger.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to catalog evidence: {str(e)}", "danger")

    return redirect(url_for("cases.case_detail", case_id=case_id))


@cases_bp.route("/<int:case_id>/add-note", methods=["POST"])
@login_required
def add_note(case_id):
    case = Case.query.get_or_404(case_id)
    allowed, reason = can_access_case(current_user, case, action="edit")
    if not allowed:
        flash(reason, "danger")
        abort(403, description=reason)

    note_title = request.form.get("note_title", "").strip()
    note_body = request.form.get("note_body", "").strip()
    is_confidential = bool(request.form.get("is_confidential"))

    if not note_title or not note_body:
        flash("Note title and body are required.", "warning")
        return redirect(url_for("cases.case_detail", case_id=case_id))

    note = InvestigationNote(
        case_id=case_id,
        author_id=current_user.user_id,
        note_title=note_title,
        note_body=note_body,
        is_confidential=is_confidential,
        logged_at=datetime.utcnow()
    )

    try:
        db.session.add(note)
        db.session.commit()
        flash("Investigation diary entry recorded.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Failed to record note: {str(e)}", "danger")

    return redirect(url_for("cases.case_detail", case_id=case_id))

