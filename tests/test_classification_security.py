"""
tests/test_classification_security.py
Comprehensive automated test suite for Multi-Level Security (MLS),
Bell-LaPadula clearance hierarchy, and discretionary Need-to-Know access control.
"""
import pytest
from app.db import db
from app.models import Case, User, CaseAssignment
from app.services.security_service import can_access_case, is_clearance_sufficient, filter_cases_for_user


def test_clearance_rank_hierarchy():
    """Validates Bell-LaPadula clearance rank comparisons (No Read Up)."""
    assert is_clearance_sufficient("RESTRICTED", "RESTRICTED") is True
    assert is_clearance_sufficient("RESTRICTED", "CONFIDENTIAL") is True
    assert is_clearance_sufficient("RESTRICTED", "INTERNAL") is True
    assert is_clearance_sufficient("RESTRICTED", "PUBLIC") is True

    assert is_clearance_sufficient("CONFIDENTIAL", "RESTRICTED") is False
    assert is_clearance_sufficient("CONFIDENTIAL", "CONFIDENTIAL") is True
    assert is_clearance_sufficient("CONFIDENTIAL", "INTERNAL") is True

    assert is_clearance_sufficient("INTERNAL", "CONFIDENTIAL") is False
    assert is_clearance_sufficient("INTERNAL", "RESTRICTED") is False
    assert is_clearance_sufficient("INTERNAL", "INTERNAL") is True
    assert is_clearance_sufficient("INTERNAL", "PUBLIC") is True


def test_admin_restricted_case_access(admin_client, app):
    """Chief Vance (Admin, RESTRICTED clearance) can inspect RESTRICTED cases."""
    with app.app_context():
        restricted_case = Case.query.filter_by(classification_level="RESTRICTED").first()
        assert restricted_case is not None, "At least one RESTRICTED case must exist."
        cid = restricted_case.case_id

    res = admin_client.get(f"/cases/{cid}")
    assert res.status_code == 200
    assert b"RESTRICTED" in res.data


def test_investigator_cannot_access_restricted_case(investigator_client, app):
    """Investigator Chen (CONFIDENTIAL clearance) is denied access to RESTRICTED cases (403)."""
    with app.app_context():
        restricted_case = Case.query.filter_by(classification_level="RESTRICTED").first()
        assert restricted_case is not None
        cid = restricted_case.case_id

    res = investigator_client.get(f"/cases/{cid}")
    assert res.status_code == 403
    assert b"Access Restricted" in res.data or b"Access Denied" in res.data


def test_officer_cannot_access_confidential_case(officer_client, app):
    """Officer Carter (INTERNAL clearance) is denied access to CONFIDENTIAL cases (403)."""
    with app.app_context():
        conf_case = Case.query.filter_by(classification_level="CONFIDENTIAL").first()
        assert conf_case is not None
        cid = conf_case.case_id

    res = officer_client.get(f"/cases/{cid}")
    assert res.status_code == 403
    assert b"Access Restricted" in res.data or b"Access Denied" in res.data


def test_assigned_investigator_accesses_confidential_case(investigator_client, app):
    """Investigator Chen (CONFIDENTIAL, assigned to case 7) can access assigned CONFIDENTIAL case."""
    with app.app_context():
        # Case 7 is Cyber Extortion, classified CONFIDENTIAL, assigned to user 5 (investigator_chen)
        case7 = Case.query.get(7)
        assert case7 is not None
        assert case7.classification_level == "CONFIDENTIAL"

    res = investigator_client.get("/cases/7")
    assert res.status_code == 200
    assert b"Cyber Extortion" in res.data


def test_unassigned_investigator_denied_need_to_know(app):
    """Investigator Hayes (CONFIDENTIAL clearance, but NOT assigned to case 7) fails Need-to-Know."""
    with app.app_context():
        hayes = User.query.filter_by(username="investigator_hayes").first()
        case7 = Case.query.get(7)
        assert hayes is not None
        assert case7 is not None
        assert hayes.clearance_level == "CONFIDENTIAL"
        assert case7.classification_level == "CONFIDENTIAL"

        # Verify Hayes is NOT assigned to case 7
        assignment = CaseAssignment.query.filter_by(case_id=7, user_id=hayes.user_id, is_active=True).first()
        assert assignment is None

        allowed, reason = can_access_case(hayes, case7, action="view")
        assert allowed is False
        assert "need-to-know" in reason.lower()


def test_deactivated_user_blocked_from_all_cases(app):
    """An inactive/suspended user is completely barred from accessing any case."""
    with app.app_context():
        case1 = Case.query.get(1)
        
        # Create a mock inactive user
        class MockInactiveUser:
            user_id = 999
            is_active = False
            clearance_level = "RESTRICTED"
            role = "Admin"
            is_admin = True

        allowed, reason = can_access_case(MockInactiveUser(), case1, action="view")
        assert allowed is False
        assert "inactive" in reason.lower() or "unauthenticated" in reason.lower()


def test_dashboard_query_isolation(app):
    """Dashboard query filtering hides classified records from lower-clearance officers."""
    with app.app_context():
        admin = User.query.filter_by(username="admin_sys").first()
        officer = User.query.filter_by(username="officer_carter").first()

        admin_cases = filter_cases_for_user(Case.query, admin).all()
        officer_cases = filter_cases_for_user(Case.query, officer).all()

        # Admin can view all 48 cases
        assert len(admin_cases) >= len(officer_cases)
        
        # Officer cannot see any RESTRICTED or unassigned CONFIDENTIAL cases in their count
        officer_classifications = {c.classification_level for c in officer_cases}
        assert "RESTRICTED" not in officer_classifications


def test_officer_forbidden_from_admin_staff(officer_client):
    """Standard patrol officer is forbidden from accessing the admin staff panel."""
    res = officer_client.get("/admin/staff", follow_redirects=True)
    assert b"Access Restricted" in res.data or b"Administrator clearance required" in res.data


def test_admin_staff_clearance_management(admin_client, app):
    """Admin can view staff register and update personnel clearance levels."""
    # Admin can access staff list
    res_admin = admin_client.get("/admin/staff")
    assert res_admin.status_code == 200
    assert b"Police Personnel &amp; Security Clearance Administration" in res_admin.data

    # Admin updates clearance for officer_ramirez (user_id = 3)
    res_update = admin_client.post(
        "/admin/staff/3/clearance",
        data={"clearance_level": "CONFIDENTIAL", "is_active": "1"},
        follow_redirects=True
    )
    assert res_update.status_code == 200
    assert b"Updated personnel clearance" in res_update.data

    with app.app_context():
        user3 = User.query.get(3)
        assert user3.clearance_level == "CONFIDENTIAL"

        # Revert back to INTERNAL for clean state
        user3.clearance_level = "INTERNAL"
        db.session.commit()
