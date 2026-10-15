"""
tests/conftest.py
Pytest fixtures for the Criminal Case Management & Crime Analytics System.
"""
import pytest
from app import create_app
from app.db import db
from app.models import User


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app


@pytest.fixture(autouse=True)
def app_context(app):
    with app.app_context():
        yield



@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def admin_client(app):
    c = app.test_client()
    c.post("/login", data={"username": "admin_sys", "password": "DemoPass123!"}, follow_redirects=True)
    return c


@pytest.fixture(scope="function")
def officer_client(app):
    c = app.test_client()
    c.post("/login", data={"username": "officer_carter", "password": "DemoPass123!"}, follow_redirects=True)
    return c


@pytest.fixture(scope="function")
def investigator_client(app):
    c = app.test_client()
    c.post("/login", data={"username": "investigator_chen", "password": "DemoPass123!"}, follow_redirects=True)
    return c

