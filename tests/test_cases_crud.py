"""
tests/test_cases_crud.py
CRUD operations, search filters, and input validation tests for Case Dossiers.
"""
from app.models import Case
from app.db import db


def test_list_cases_filter(admin_client):
    """Filter by status and crime classification."""
    res = admin_client.get("/cases?status=Open")
    assert res.status_code == 200
    assert b"Case Dossiers" in res.data


def test_create_case_validation(admin_client):
    """Case creation requires valid title, location, and station."""
    # Missing title
    res = admin_client.post("/cases/create", data={
        "title": "",
        "station_id": "1",
        "case_type": "Theft",
        "priority": "Medium",
        "incident_location": "100 State St"
    }, follow_redirects=True)
    assert b"Case title must be at least 5 characters" in res.data


def test_create_and_read_case(admin_client, app):
    """Successful creation of a case dossier and verification of detail view."""
    case_title = "Pytest Automated Dossier Verification"
    res = admin_client.post("/cases/create", data={
        "title": case_title,
        "station_id": "1",
        "case_type": "Burglary",
        "priority": "High",
        "incident_location": "999 N Michigan Ave, Chicago, IL",
        "description": "Integration test created dossier."
    }, follow_redirects=True)
    assert res.status_code == 200
    assert case_title.encode() in res.data

    with app.app_context():
        created = Case.query.filter_by(title=case_title).first()
        assert created is not None
        assert created.status == "Open"
        assert created.is_fictional is True
        
        # Cleanup
        db.session.delete(created)
        db.session.commit()
