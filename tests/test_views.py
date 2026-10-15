"""
tests/test_views.py
Automated tests for compiled database views (v_case_summary, v_officer_workload).
"""
from sqlalchemy import text
from app.db import db
from app.models import VCaseSummary, VOfficerWorkload


def test_case_summary_query(app):
    """v_case_summary view exposes assigned_officer_count, evidence_count, and days_elapsed."""
    query_sql = """
        SELECT 
            case_number, title, case_type, status, priority,
            station_name, lead_investigator, assigned_officer_count,
            evidence_count, days_elapsed
        FROM v_case_summary
        ORDER BY days_elapsed DESC
        LIMIT 10;
    """
    res = db.session.execute(text(query_sql)).fetchall()
    assert len(res) > 0
    first_row = res[0]
    # Verify all expected columns are returned and indexed properly
    assert hasattr(first_row, "assigned_officer_count")
    assert hasattr(first_row, "evidence_count")
    assert hasattr(first_row, "days_elapsed")
    assert hasattr(first_row, "case_number")


def test_case_summary_orm_model(app):
    """SQLAlchemy VCaseSummary model queries without column mapping mismatches."""
    records = VCaseSummary.query.limit(5).all()
    assert len(records) > 0
    first = records[0]
    assert first.case_number is not None
    assert first.assigned_officer_count is not None
    assert first.evidence_count is not None
    assert first.days_elapsed is not None


def test_officer_workload_orm_model(app):
    """SQLAlchemy VOfficerWorkload model queries without column mapping mismatches."""
    records = VOfficerWorkload.query.all()
    assert len(records) > 0
    first = records[0]
    assert first.user_id is not None
    assert hasattr(first, "officer_name")
    assert hasattr(first, "active_cases")
    assert hasattr(first, "lead_investigator_cases")


def test_sql_demo_views_tab_http(admin_client):
    """GET /sql-demo?tab=views executes successfully with HTTP 200 and renders result table."""
    res = admin_client.get("/sql-demo?tab=views")
    assert res.status_code == 200
    assert b"Query Execution Error" not in res.data
    assert b"assigned_officer_count" in res.data
    assert b"days_elapsed" in res.data
