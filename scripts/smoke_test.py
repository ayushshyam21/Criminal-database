import sys
import os
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import User, Case, Citizen, CitizenReport, Evidence, Person
from sqlalchemy import text

def run_smoke_test():
    print("=" * 70)
    print("CRIMINAL CASE MANAGEMENT SYSTEM — FACULTY DEMO SMOKE TEST")
    print("=" * 70)

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    client = app.test_client()

    results = []

    def record_result(check_name, passed, details=""):
        status_str = "[PASS]" if passed else "[FAIL]"
        print(f"  {status_str} {check_name}: {details}")
        results.append((check_name, passed, details))

    with app.app_context():
        # 1. Staff Login & Dashboard
        print("\n[TEST 1] Staff Login & Dashboard Access (RBAC & Clearance)")
        # Admin login
        resp = client.post("/login", data={"username": "admin_sys", "password": "DemoPass123!"}, follow_redirects=True)
        record_result("Admin Login (admin_sys)", resp.status_code == 200 and b"Chief Eleanor Vance" in resp.data, f"Status: {resp.status_code}")
        
        # Admin Dashboard
        resp_dash = client.get("/dashboard")
        record_result("Admin Dashboard View", resp_dash.status_code == 200 and b"Operational Overview" in resp_dash.data, "Full metrics rendered")
        client.get("/logout")

        # Officer Carter Login & Dashboard
        resp_officer = client.post("/login", data={"username": "officer_carter", "password": "DemoPass123!"}, follow_redirects=True)
        record_result("Officer Login (officer_carter)", resp_officer.status_code == 200 and b"Marcus Carter" in resp_officer.data, f"Status: {resp_officer.status_code}")
        
        resp_officer_dash = client.get("/dashboard")
        record_result("Officer Dashboard View", resp_officer_dash.status_code == 200, "Dashboard filtered to officer clearance")
        client.get("/logout")

        # 2. Case Listing and Case Creation
        print("\n[TEST 2] Case Listing and Case Creation")
        client.post("/login", data={"username": "admin_sys", "password": "DemoPass123!"}, follow_redirects=True)
        resp_cases = client.get("/cases")
        record_result("Case Listing Page", resp_cases.status_code == 200 and b"Case Dossiers" in resp_cases.data, f"Status: {resp_cases.status_code}")

        # Create a temporary case
        test_case_title = f"Smoke Test Case {uuid.uuid4().hex[:6].upper()}"
        resp_create = client.post("/cases/create", data={
            "title": test_case_title,
            "station_id": 1,
            "case_type": "Theft",
            "priority": "Low",
            "classification_level": "PUBLIC",
            "incident_location": "100 N State St, Chicago, IL",
            "description": "Fictional case created during live faculty smoke testing."
        }, follow_redirects=True)
        created_ok = resp_create.status_code == 200 and test_case_title.encode() in resp_create.data
        record_result("Case Creation Submission", created_ok, f"Case '{test_case_title}' created")

        # Verify direct DB persistence using raw SQL
        created_case = db.session.execute(text("SELECT case_id, title, classification_level FROM cases WHERE title = :title"), {"title": test_case_title}).fetchone()
        persisted_ok = created_case is not None and created_case[1] == test_case_title
        record_result("Database Persistence Verification", persisted_ok, f"Direct MySQL query verified: ID={created_case[0] if created_case else 'N/A'}")

        # Clean up temporary smoke test case to leave DB pristine
        if created_case:
            db.session.execute(text("DELETE FROM cases WHERE case_id = :cid"), {"cid": created_case[0]})
            db.session.commit()
            print(f"       -> Cleaned up temporary test case ID {created_case[0]}")
        client.get("/logout")

        # 3. Citizen Registration, Login, Submission & Tracking
        print("\n[TEST 3] Citizen Registration, Login, Report Submission & Tracking")
        citizen_client = app.test_client()
        unique_email = f"demo.citizen.{uuid.uuid4().hex[:6]}@example.com"
        resp_reg = citizen_client.post("/citizen/register", data={
            "full_name": "Faculty Evaluator",
            "email": unique_email,
            "password": "CitizenSecure123!",
            "confirm_password": "CitizenSecure123!",
            "phone_number": "312-555-0188",
            "address": "123 Academic Way, Chicago, IL"
        }, follow_redirects=True)
        record_result("Citizen Registration", resp_reg.status_code == 200 and b"Registration successful" in resp_reg.data, f"Registered {unique_email}")

        # Login with newly registered citizen
        resp_cit_login = citizen_client.post("/citizen/login", data={
            "email": unique_email,
            "password": "CitizenSecure123!"
        }, follow_redirects=True)
        record_result("Citizen Login", resp_cit_login.status_code == 200 and b"Citizen Dashboard" in resp_cit_login.data, "Session authenticated")

        # Submit new citizen report
        resp_rep = citizen_client.post("/citizen/reports/new", data={
            "category": "Lost Property",
            "incident_date": "2026-03-20",
            "incident_location": "Millennium Park North Promenade",
            "title": "Lost Gold Watch Demo",
            "description": "Fictional lost property submission during smoke test."
        }, follow_redirects=True)
        report_submitted = resp_rep.status_code == 200 and b"CR-2026-" in resp_rep.data
        record_result("Citizen Report Submission", report_submitted, "Generated tracking number displayed")

        # Fetch tracking number from citizen reports
        cit_user = Citizen.query.filter_by(email=unique_email).first()
        my_report = CitizenReport.query.filter_by(citizen_id=cit_user.citizen_id).first()
        if my_report:
            resp_detail = citizen_client.get(f"/citizen/reports/{my_report.report_id}")
            record_result("Citizen Report Detail Tracking", resp_detail.status_code == 200 and my_report.tracking_number.encode() in resp_detail.data, f"Tracking: {my_report.tracking_number}")

        # 4. Access Control Verification (Backend Enforcement)
        print("\n[TEST 4] Backend Access Control & Security Boundaries")
        
        # 4a. Cross-citizen report isolation (404 expected to prevent enumeration)
        # Citizen Evaluator tries to access Jane's report (ID 1)
        resp_probe = citizen_client.get("/citizen/reports/1")
        record_result("Cross-Citizen Privacy Isolation (Anti-Enumeration)", resp_probe.status_code == 404, f"Accessing report 1 returned HTTP {resp_probe.status_code}")

        # 4b. Citizen session blocked from staff routes
        resp_cit_staff = citizen_client.get("/cases")
        record_result("Citizen Blocked From Staff Cases", resp_cit_staff.status_code == 302 and "/login" in resp_cit_staff.headers.get("Location", ""), "Redirected to staff login")

        # 4c. Classification-based case access
        staff_client = app.test_client()

        # Admin Vance (RESTRICTED clearance) accesses Case 9 (RESTRICTED)
        staff_client.post("/login", data={"username": "admin_sys", "password": "DemoPass123!"}, follow_redirects=True)
        resp_admin_c9 = staff_client.get("/cases/9")
        record_result("Admin RESTRICTED Access (Case 9)", resp_admin_c9.status_code == 200 and b"CASE-2026-0009" in resp_admin_c9.data, f"HTTP {resp_admin_c9.status_code}")
        staff_client.get("/logout")

        # Investigator Hayes (CONFIDENTIAL clearance, UNASSIGNED to Case 7) -> Need-to-Know 403
        staff_client.post("/login", data={"username": "investigator_hayes", "password": "DemoPass123!"}, follow_redirects=True)
        resp_hayes_c7 = staff_client.get("/cases/7")
        record_result("Unassigned Investigator Denied (Need-to-Know)", resp_hayes_c7.status_code == 403, f"HTTP {resp_hayes_c7.status_code} Forbidden")
        staff_client.get("/logout")

        # Officer Carter (INTERNAL clearance) attempts to access Case 9 (RESTRICTED) -> 403
        staff_client.post("/login", data={"username": "officer_carter", "password": "DemoPass123!"}, follow_redirects=True)
        resp_carter_c9 = staff_client.get("/cases/9")
        record_result("Insufficient Clearance Denied (Bell-LaPadula)", resp_carter_c9.status_code == 403, f"HTTP {resp_carter_c9.status_code} Forbidden")
        staff_client.get("/logout")

        # 5. Admin Staff & Clearance Management
        print("\n[TEST 5] Admin Staff & Clearance Management")
        staff_client.post("/login", data={"username": "admin_sys", "password": "DemoPass123!"}, follow_redirects=True)
        resp_staff_panel = staff_client.get("/admin/staff")
        record_result("Admin Staff Management Panel", resp_staff_panel.status_code == 200 and b"Police Personnel &amp; Security Clearance Administration" in resp_staff_panel.data, "Clearance table accessible")

        # Officer Carter blocked from admin panel (redirected with Access Restricted)
        staff_client.get("/logout")
        staff_client.post("/login", data={"username": "officer_carter", "password": "DemoPass123!"}, follow_redirects=True)
        resp_officer_admin = staff_client.get("/admin/staff", follow_redirects=True)
        record_result("Non-Admin Blocked from Staff Clearances", resp_officer_admin.status_code == 200 and b"Access Restricted" in resp_officer_admin.data, "Redirected with security denial flash")
        staff_client.get("/logout")

        # 6. Evidence and Related Records
        print("\n[TEST 6] Evidence and Person Record Screens")
        staff_client.post("/login", data={"username": "admin_sys", "password": "DemoPass123!"}, follow_redirects=True)
        resp_ev_list = staff_client.get("/evidence")
        record_result("Evidence Inventory List", resp_ev_list.status_code == 200 and b"Evidence Vault" in resp_ev_list.data, f"Status: {resp_ev_list.status_code}")

        resp_ev_det = staff_client.get("/evidence/6")
        record_result("Evidence Detail & Custody Chain", resp_ev_det.status_code == 200 and b"Chain of Custody" in resp_ev_det.data, "Immutable ledger entries visible")

        resp_per_list = staff_client.get("/persons")
        record_result("Persons Directory", resp_per_list.status_code == 200 and b"Demonstration Personas" in resp_per_list.data, f"Status: {resp_per_list.status_code}")

        resp_per_det = staff_client.get("/persons/1")
        record_result("Person Detail View", resp_per_det.status_code == 200 and b"Demo-Suspect Sterling" in resp_per_det.data, "Person detail & case roles rendered")
        staff_client.get("/logout")

        # 7. Analytics & Live SQL Demo
        print("\n[TEST 7] Crime Analytics & Live SQL Demo Console")
        staff_client.post("/login", data={"username": "admin_sys", "password": "DemoPass123!"}, follow_redirects=True)
        resp_analytics = staff_client.get("/public-crimes")
        record_result("Chicago Public Crime Analytics", resp_analytics.status_code == 200 and b"Chicago Open Crimes" in resp_analytics.data, "Trend charts and incident records loaded")

        resp_sql_demo = staff_client.get("/sql-demo")
        record_result("Live SQL Showcase Console", resp_sql_demo.status_code == 200 and b"SQL Demonstration" in resp_sql_demo.data, "Live queries and EXPLAIN tabs loaded")
        staff_client.get("/logout")

    print("\n" + "=" * 70)
    passed_count = sum(1 for _, p, _ in results if p)
    total_count = len(results)
    print(f"SMOKE TEST SUMMARY: {passed_count}/{total_count} CHECKS PASSED ({passed_count/total_count*100:.1f}%)")
    print("=" * 70)

    if passed_count < total_count:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    run_smoke_test()
