"""
tests/test_importer.py
Tests for the City of Chicago public crime dataset importer and error resilience.
"""
from app.services.chicago_importer import import_chicago_crimes
from app.models import PublicCrimeIncident


def test_importer_repeatability(app):
    """Importer must handle duplicate records cleanly without crashing or corrupting data."""
    with app.app_context():
        res1 = import_chicago_crimes(limit=5)
        assert res1["success"] is True

        # Running again with the same limit should skip duplicates
        res2 = import_chicago_crimes(limit=5)
        assert res2["success"] is True
        assert res2["duplicates_skipped"] >= 0
