"""
app/routes/sql_demo.py
Interactive Project SQL Demonstration Showcase.
Demonstrates complex JOINs, subqueries, views, stored routines, triggers,
transactions, and EXPLAIN execution plans directly in the web application.
"""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import text
from app.db import db
from app.models import AuditLog, EvidenceCustodyLog

sql_demo_bp = Blueprint("sql_demo", __name__, url_prefix="/sql-demo")


@sql_demo_bp.route("", strict_slashes=False)
@sql_demo_bp.route("/", strict_slashes=False)
@login_required
def index():
    active_tab = request.args.get("tab", "joins")
    results = {}
    query_sql = ""
    error = None

    try:
        if active_tab == "joins":
            # 1. Complex 4-Table JOIN with Aggregation
            query_sql = """
                SELECT 
                    c.case_number,
                    c.title,
                    c.status,
                    c.priority,
                    ps.station_name,
                    ps.district_code,
                    u.full_name AS creator_name,
                    COUNT(DISTINCT ca.assignment_id) AS active_officers,
                    COUNT(DISTINCT e.evidence_id) AS evidence_items
                FROM cases c
                JOIN police_stations ps ON c.station_id = ps.station_id
                JOIN users u ON c.created_by = u.user_id
                LEFT JOIN case_assignments ca ON c.case_id = ca.case_id AND ca.is_active = TRUE
                LEFT JOIN evidence e ON c.case_id = e.case_id
                GROUP BY c.case_id, c.case_number, c.title, c.status, c.priority, 
                         ps.station_name, ps.district_code, u.full_name
                ORDER BY c.date_reported DESC
                LIMIT 10;
            """
            cursor = db.session.execute(text(query_sql))
            results["columns"] = list(cursor.keys())
            results["rows"] = cursor.fetchall()

        elif active_tab == "nested":
            # 2. Correlated Subquery & Window Function
            query_sql = """
                SELECT 
                    c.case_id,
                    c.case_number,
                    c.case_type,
                    c.priority,
                    c.date_reported,
                    (SELECT COUNT(*) FROM case_persons cp WHERE cp.case_id = c.case_id) AS person_count,
                    DENSE_RANK() OVER (PARTITION BY c.case_type ORDER BY c.date_reported DESC) AS type_recency_rank
                FROM cases c
                WHERE c.status IN ('Open', 'Under Investigation')
                  AND c.case_id IN (
                      SELECT case_id FROM evidence GROUP BY case_id HAVING COUNT(*) >= 1
                  )
                ORDER BY c.case_type, type_recency_rank
                LIMIT 15;
            """
            cursor = db.session.execute(text(query_sql))
            results["columns"] = list(cursor.keys())
            results["rows"] = cursor.fetchall()

        elif active_tab == "views":
            # 3. Querying Pre-Compiled Relational Views
            query_sql = """
                SELECT 
                    case_number, title, case_type, status, priority,
                    station_name, lead_investigator, assigned_officer_count,
                    evidence_count, days_elapsed
                FROM v_case_summary
                ORDER BY days_elapsed DESC
                LIMIT 10;
            """
            cursor = db.session.execute(text(query_sql))
            results["columns"] = list(cursor.keys())
            results["rows"] = cursor.fetchall()

        elif active_tab == "routines":
            # 4. Stored Procedure & Function Showcase
            query_sql = """
                SELECT 
                    case_id,
                    case_number,
                    title,
                    status,
                    date_reported,
                    date_closed,
                    fn_case_duration(case_id) AS calculated_duration_days
                FROM cases
                WHERE case_id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
                ORDER BY case_id;
            """
            cursor = db.session.execute(text(query_sql))
            results["columns"] = list(cursor.keys())
            results["rows"] = cursor.fetchall()

        elif active_tab == "triggers":
            # 5. Live Inspection of Trigger-Generated Ledgers
            audit_records = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
            custody_records = EvidenceCustodyLog.query.order_by(EvidenceCustodyLog.logged_at.desc()).limit(10).all()
            return render_template(
                "sql_demo/index.html",
                active_tab=active_tab,
                audit_records=audit_records,
                custody_records=custody_records
            )

        elif active_tab == "explain":
            # 6. EXPLAIN Benchmark Query
            query_sql = """
                EXPLAIN
                SELECT c.case_id, c.case_number, c.title, c.priority
                FROM cases c
                WHERE c.status = 'Under Investigation' AND c.priority = 'Critical';
            """
            cursor = db.session.execute(text(query_sql))
            results["columns"] = list(cursor.keys())
            results["rows"] = cursor.fetchall()

    except Exception as e:
        error = str(e)

    return render_template(
        "sql_demo/index.html",
        active_tab=active_tab,
        query_sql=query_sql.strip(),
        results=results,
        error=error
    )
