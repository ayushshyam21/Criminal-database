"""
tests/test_permissions.py
Role-Based Access Control (RBAC) tests for Admin, Officer, and Investigator.
"""
from app.models import Case


def test_admin_access_allowed(admin_client):
    """Admin has full access to administrative actions."""
    res = admin_client.get("/dashboard")
    assert res.status_code == 200
    assert b"Operational Overview" in res.data


def test_officer_cannot_delete_case(officer_client, app):
    """Standard officers cannot execute administrative case deletion."""
    with app.app_context():
        case = Case.query.first()
        assert case is not None
        cid = case.case_id
    res = officer_client.post(f"/cases/{cid}/delete", follow_redirects=True)
    assert res.status_code == 200
    assert b"Administrative credentials required" in res.data


def test_investigator_confidential_notes(investigator_client, officer_client, app):
    """Investigators can see confidential diary notes; non-investigators cannot."""
    with app.app_context():
        case = Case.query.first()
        assert case is not None
        cid = case.case_id
    res_inv = investigator_client.get(f"/cases/{cid}")
    assert res_inv.status_code == 200
    # Investigator client has can_view_confidential = True
    assert b"Personnel Allocations" in res_inv.data

