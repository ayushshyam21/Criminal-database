"""
tests/test_auth.py
Automated tests for user authentication, session lifecycle, and credential security.
"""
def test_unauthenticated_redirect(client):
    """Unauthenticated access to protected routes must redirect to /login."""
    res = client.get("/dashboard", follow_redirects=False)
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]


def test_valid_admin_login(client):
    """Valid credentials authenticate and redirect to operations dashboard."""
    res = client.post("/login", data={"username": "admin_sys", "password": "DemoPass123!"}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Operational Overview" in res.data
    assert b"Chief Eleanor Vance" in res.data


def test_invalid_password(client):
    """Invalid credentials must be rejected with flash error."""
    client.get("/logout")
    res = client.post("/login", data={"username": "admin_sys", "password": "WrongPassword!"}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Invalid username or password" in res.data


def test_logout(admin_client):
    """Logout invalidates session and redirects to login."""
    res = admin_client.get("/logout", follow_redirects=True)
    assert res.status_code == 200
    assert b"signed out successfully" in res.data
