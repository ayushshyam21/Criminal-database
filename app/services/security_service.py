"""
app/services/security_service.py
Enforces multi-level security clearance, Bell-LaPadula access rules,
and discretionary need-to-know verification for criminal cases and evidence.
"""
from sqlalchemy import or_
from app.db import db
from app.models import Case, CaseAssignment, VCaseSummary

CLEARANCE_RANKS = {
    "PUBLIC": 1,
    "INTERNAL": 2,
    "CONFIDENTIAL": 3,
    "RESTRICTED": 4
}

CLASSIFICATION_BADGES = {
    "PUBLIC": "bg-secondary",
    "INTERNAL": "bg-primary",
    "CONFIDENTIAL": "bg-warning text-dark",
    "RESTRICTED": "bg-danger"
}


def get_clearance_rank(level: str) -> int:
    return CLEARANCE_RANKS.get((level or "").upper(), 1)


def get_classification_rank(level: str) -> int:
    return CLEARANCE_RANKS.get((level or "").upper(), 2)


def is_clearance_sufficient(user_clearance: str, case_classification: str) -> bool:
    """
    Bell-LaPadula Simple Security Property (No Read Up):
    A user can only read a case if their clearance rank is >= the case's classification rank.
    """
    return get_clearance_rank(user_clearance) >= get_classification_rank(case_classification)


def has_need_to_know(user, case) -> bool:
    """
    Discretionary Access Control (Need-to-Know):
    1. Administrators have global supervisory oversight across all accessible cases.
    2. PUBLIC and INTERNAL cases are routine operational records accessible to all active staff.
    3. CONFIDENTIAL and RESTRICTED classified cases strictly require active assignment (is_active=True)
       or original case authorship.
    """
    if not user or not user.is_active:
        return False

    if getattr(user, "is_admin", False):
        return True

    classification = getattr(case, "classification_level", "INTERNAL")
    if classification in ("PUBLIC", "INTERNAL"):
        return True

    # For classified material (CONFIDENTIAL / RESTRICTED), enforce strict need-to-know:
    if case.created_by == user.user_id:
        return True

    active_assignment = CaseAssignment.query.filter_by(
        case_id=case.case_id,
        user_id=user.user_id,
        is_active=True
    ).first()

    return active_assignment is not None


def can_access_case(user, case, action: str = "view") -> tuple[bool, str]:
    """
    Comprehensive access authorization evaluating both clearance rank and need-to-know.
    Returns (authorized: bool, reason: str).
    """
    if not user or not user.is_active:
        return False, "User account is inactive or unauthenticated."

    case_classification = getattr(case, "classification_level", "INTERNAL")
    user_clearance = getattr(user, "clearance_level", "INTERNAL")

    # 1. Bell-LaPadula Clearance Check (No Read Up)
    if not is_clearance_sufficient(user_clearance, case_classification):
        return (
            False,
            f"Access Denied: Your security clearance '{user_clearance}' is insufficient "
            f"for this '{case_classification}' classified case."
        )

    # 2. Discretionary Need-to-Know Check for Classified Material
    if not has_need_to_know(user, case):
        return (
            False,
            "Access Denied: Discretionary need-to-know requirement not met. "
            "You are not actively assigned to this classified case."
        )

    # 3. Action-Specific Role Privileges
    if action == "delete":
        if not getattr(user, "is_admin", False):
            return False, "Permission Denied: Administrative credentials required to purge case records."

    if action == "edit":
        if not (getattr(user, "is_admin", False) or getattr(user, "is_investigator", False) or case.created_by == user.user_id):
            return False, "Permission Denied: You do not have editorial authority on this case."

    return True, "Authorized."


def filter_cases_for_user(query, user, model=Case):
    """
    Filters a SQLAlchemy query at the database level so staff never see
    records beyond their clearance rank or discretionary assignment scope.
    """
    if not user or not user.is_active:
        return query.filter(db.false())

    user_clearance = getattr(user, "clearance_level", "INTERNAL")
    user_rank = get_clearance_rank(user_clearance)

    permitted_levels = [lvl for lvl, r in CLEARANCE_RANKS.items() if r <= user_rank]

    # Model classification column check (No Read Up)
    if hasattr(model, "classification_level"):
        query = query.filter(model.classification_level.in_(permitted_levels))

    # Admins have department-wide oversight of all permitted clearance cases
    if getattr(user, "is_admin", False):
        return query

    # Non-admin staff:
    # PUBLIC and INTERNAL cases are visible; CONFIDENTIAL/RESTRICTED require assignment or authorship
    if model == Case:
        assigned_case_ids = (
            db.select(CaseAssignment.case_id)
            .where(CaseAssignment.user_id == user.user_id, CaseAssignment.is_active == True)
        )
        query = query.filter(
            or_(
                Case.classification_level.in_(["PUBLIC", "INTERNAL"]),
                Case.case_id.in_(assigned_case_ids),
                Case.created_by == user.user_id
            )
        )
    elif model == VCaseSummary:
        assigned_case_ids = (
            db.select(CaseAssignment.case_id)
            .where(CaseAssignment.user_id == user.user_id, CaseAssignment.is_active == True)
        )
        query = query.filter(
            or_(
                VCaseSummary.classification_level.in_(["PUBLIC", "INTERNAL"]),
                VCaseSummary.case_id.in_(assigned_case_ids)
            )
        )

    return query
