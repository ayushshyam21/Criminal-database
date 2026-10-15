"""
run.py
Main entrypoint for the Criminal Case Management & Crime Analytics System.
"""
import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1")
    
    print("=" * 70)
    print("CRIMINAL CASE MANAGEMENT & CRIME ANALYTICS SYSTEM (PROJECT EVALUATION)")
    print(f"Local Server Live at: http://127.0.0.1:{port}")
    print("Runtime Database User: crimedb_app (Least Privilege)")
    print("Demo Admin User: admin_sys | Password: DemoPass123!")
    print("=" * 70)
    
    app.run(host="127.0.0.1", port=port, debug=debug)
