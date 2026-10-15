"""
tests/test_citizen_portal.py
Automated test suite verifying the Citizen Portal:
registration, authentication, non-emergency reporting, unique tracking reference,
cross-citizen privacy isolation, and separation from internal police records.
"""
from datetime import date
from app.db import db
from app.models import Citizen, CitizenReport


def test_unauthenticated_citizen_redirect(client):
    """Accessing protected citizen routes without session redirects to citizen login."""
    res = client.get("/citizen/dashboard", follow_redirects=False)
    assert res.status_code == 302
    assert "/citizen/login" in res.headers["Location"]


def test_citizen_registration_and_login(client, app):
    """Validates citizen account creation with secure hash and subsequent sign-in."""
    import uuid
    test_email = f"citizen.unit.{uuid.uuid4().hex[:8]}@example.com"
    test_pass = "SecurePass123!"

    # 1. Registration
    res_reg = client.post(
        "/citizen/register",
        data={
            "full_name": "Test Citizen Unit",
            "email": test_email,
            "password": test_pass,
            "confirm_password": test_pass,
            "phone_number": "312-555-0999",
            "address": "Fictional 123 Test St, Chicago, IL"
        },
        follow_redirects=True
    )
    assert res_reg.status_code == 200
    assert b"Registration successful" in res_reg.data

    # Verify password is not stored in plaintext
    with app.app_context():
        new_cit = Citizen.query.filter_by(email=test_email).first()
        assert new_cit is not None
        assert new_cit.password_hash != test_pass
        assert new_cit.check_password(test_pass) is True

    # 2. Login
    res_login = client.post(
        "/citizen/login",
        data={"email": test_email, "password": test_pass},
        follow_redirects=True
    )
    assert res_login.status_code == 200
    assert b"Citizen Dashboard" in res_login.data
    assert b"Test Citizen Unit" in res_login.data

    # 3. Logout
    res_logout = client.get("/citizen/logout", follow_redirects=True)
    assert res_logout.status_code == 200
    assert b"signed out of the Citizen Portal" in res_logout.data


def test_citizen_login_invalid_password(client):
    """Invalid password rejection on citizen login."""
    res = client.post(
        "/citizen/login",
        data={"email": "citizen.jane@example.com", "password": "WrongPassword999!"},
        follow_redirects=True
    )
    assert res.status_code == 200
    assert b"Invalid email or password" in res.data


def test_citizen_report_submission_and_tracking(client, app):
    """Submitting a citizen demo report creates a unique tracking code and report record."""
    # Login as pre-seeded demo citizen Jane
    client.post(
        "/citizen/login",
        data={"email": "citizen.jane@example.com", "password": "Citizen123!"},
        follow_redirects=True
    )

    # Submit new incident report
    import uuid
    unique_title = f"Lost Silver Wristwatch {uuid.uuid4().hex[:6]}"
    res_submit = client.post(
        "/citizen/reports/new",
        data={
            "category": "Lost Property",
            "incident_date": date.today().isoformat(),
            "incident_location": "Millennium Park Pavilion, Chicago, IL",
            "title": unique_title,
            "description": "Lost an engraved silver analog wristwatch near the pavilion concert seating around 4 PM."
        },
        follow_redirects=True
    )
    assert res_submit.status_code == 200
    assert b"Your report has been submitted successfully" in res_submit.data
    assert b"CR-2026-" in res_submit.data

    with app.app_context():
        report = CitizenReport.query.filter(
            CitizenReport.title == unique_title
        ).first()
        assert report is not None
        assert report.tracking_number.startswith("CR-2026-")
        assert report.status == "Submitted"
        assert report.is_demo_submission is True


def test_cross_citizen_privacy_isolation(client, app):
    """Citizen B cannot view or probe reports filed by Citizen A (returns 404)."""
    # 1. Create Report for Citizen A (Jane, ID 1)
    with app.app_context():
        report_a = CitizenReport.query.filter_by(citizen_id=1).first()
        assert report_a is not None
        report_a_id = report_a.report_id

    # 2. Register & Login as Citizen B
    citizen_b_email = "citizen.bob@example.com"
    with app.app_context():
        if not Citizen.query.filter_by(email=citizen_b_email).first():
            b = Citizen(email=citizen_b_email, full_name="Bob Test", is_active=True)
            b.set_password("Citizen123!")
            db.session.add(b)
            db.session.commit()

    client.post(
        "/citizen/login",
        data={"email": citizen_b_email, "password": "Citizen123!"},
        follow_redirects=True
    )

    # 3. Citizen B tries to inspect Citizen A's report
    res = client.get(f"/citizen/reports/{report_a_id}")
    assert res.status_code == 404
    assert b"Dossier or Record Not Found" in res.data or b"404" in res.data


def test_citizen_session_cannot_access_staff_routes(client):
    """A signed-in citizen cannot access internal police staff routes (/cases, /evidence, /dashboard)."""
    # Login as citizen
    client.post(
        "/citizen/login",
        data={"email": "citizen.jane@example.com", "password": "Citizen123!"},
        follow_redirects=True
    )

    # Attempt to hit staff routes
    for endpoint in ["/dashboard", "/cases", "/evidence", "/persons"]:
        res = client.get(endpoint, follow_redirects=False)
        # Should be redirected to staff login (/login), NOT granted access
        assert res.status_code == 302
        assert "/login" in res.headers["Location"]
