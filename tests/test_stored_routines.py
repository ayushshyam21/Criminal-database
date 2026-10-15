"""
tests/test_stored_routines.py
Tests for Stored Procedure (sp_assign_case) and Stored Function (fn_case_duration).
"""
from sqlalchemy import text
from app.db import db
from app.models import Case, CaseAssignment


def test_stored_function_duration(app):
    """fn_case_duration must return non-null positive elapsed days for existing cases."""
    first_case = Case.query.first()
    assert first_case is not None
    res = db.session.execute(text("SELECT fn_case_duration(:cid) AS days;"), {"cid": first_case.case_id}).fetchone()
    assert res[0] is not None
    assert res[0] >= 0

    # Nonexistent case must return NULL
    res_null = db.session.execute(text("SELECT fn_case_duration(999999) AS days;")).fetchone()
    assert res_null[0] is None


def test_stored_procedure_assignment(admin_client, app):
    """sp_assign_case assigns personnel and returns SUCCESS code."""
    target_case = Case.query.filter(Case.status != "Closed").first()
    assert target_case is not None
    cid = target_case.case_id
    res = admin_client.post(f"/cases/{cid}/assign", data={
        "user_id": "6",  # Det. Rachel Hayes
        "role": "Assisting Officer",
        "notes": "Pytest procedure execution"
    }, follow_redirects=True)
    assert res.status_code == 200
    assert b"Personnel assignment completed" in res.data or b"allocated" in res.data


