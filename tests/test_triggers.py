"""
tests/test_triggers.py
Tests verifying that MySQL Triggers write to immutable audit and custody ledgers.
"""
from app.models import Case, Evidence, AuditLog, EvidenceCustodyLog
from app.db import db


def test_case_status_audit_trigger(admin_client, app):
    """Updating case priority/status must fire trg_cases_status_audit into audit_log."""
    c = Case.query.first()
    assert c is not None
    cid = c.case_id
    original_status = c.status
    original_priority = c.priority

    # Change priority to trigger audit
    new_priority = "Critical" if original_priority != "Critical" else "High"
    admin_client.post(f"/cases/{cid}/edit", data={
        "title": c.title,
        "case_type": c.case_type,
        "status": c.status,
        "priority": new_priority,
        "incident_location": c.incident_location or "400 N Michigan Ave, Chicago, IL"
    }, follow_redirects=True)

    log = AuditLog.query.filter_by(table_name="cases", record_id=cid).order_by(AuditLog.log_id.desc()).first()
    assert log is not None
    assert log.operation_type == "UPDATE"
    assert log.performed_by == "admin_sys"


def test_evidence_custody_transfer_trigger(admin_client, app):
    """Transferring evidence location/status must fire trg_evidence_custody_update."""
    ev = Evidence.query.first()
    assert ev is not None
    ev_id = ev.evidence_id
    initial_log_count = EvidenceCustodyLog.query.filter_by(evidence_id=ev_id).count()

    new_loc = "CPD Primary Vault Alpha" if ev.current_storage_location != "CPD Primary Vault Alpha" else "CPD Secondary Lockup B-12"
    new_stat = "Court Presentation" if ev.current_custody_status != "Court Presentation" else "Vault Storage"

    admin_client.post(f"/evidence/{ev_id}/transfer", data={
        "new_status": new_stat,
        "new_location": new_loc,
        "reason": "Automated trigger validation test"
    }, follow_redirects=True)

    new_log_count = EvidenceCustodyLog.query.filter_by(evidence_id=ev_id).count()
    assert new_log_count > initial_log_count
    latest = EvidenceCustodyLog.query.filter_by(evidence_id=ev_id).order_by(EvidenceCustodyLog.custody_id.desc()).first()
    assert latest.to_location == new_loc
    assert latest.handled_by is not None


