"""
Playwright E2E test fixtures for TimeHit.

Starts a Django dev server on port 8001 with Postgres,
creates a superuser, and provides a logged-in page fixture.
"""
import os
import signal
import subprocess
import sys
import time

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SERVER_URL = "http://localhost:8001"
SUPERUSER_EMAIL = "a@a.a"
SUPERUSER_PASSWORD = "a"
MANAGE_PY = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "agency_platform",
    "manage.py",
)

# Environment for the Django process
DJANGO_ENV = {
    **os.environ,
    "DJANGO_SETTINGS_MODULE": "config.settings.dev",
    "DB_NAME": "timehit",
    "DB_USER": "timehit",
    "DB_PASSWORD": "a",
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
}


# ---------------------------------------------------------------------------
# Session-scoped: Django server + superuser
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def _run_migrations():
    """Run migrations before starting the server."""
    subprocess.run(
        [sys.executable, MANAGE_PY, "migrate", "--run-syncdb"],
        env=DJANGO_ENV,
        check=True,
        capture_output=True,
    )


@pytest.fixture(scope="session")
def _create_superuser(_run_migrations):
    """Ensure the test superuser exists (idempotent)."""
    subprocess.run(
        [
            sys.executable,
            MANAGE_PY,
            "shell",
            "-c",
            (
                "from apps.users.models import User, UserRole; "
                f"User.objects.filter(email='{SUPERUSER_EMAIL}').exists() or "
                f"User.objects.create_superuser("
                f"email='{SUPERUSER_EMAIL}', password='{SUPERUSER_PASSWORD}', "
                f"first_name='Admin', last_name='Test', role=UserRole.ADMIN)"
            ),
        ],
        env=DJANGO_ENV,
        check=True,
        capture_output=True,
    )


@pytest.fixture(scope="session")
def django_server(_create_superuser):
    """Start Django dev server on port 8001 for the test session."""
    proc = subprocess.Popen(
        [sys.executable, MANAGE_PY, "runserver", "8001", "--noreload"],
        env=DJANGO_ENV,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for the server to be ready
    import urllib.request
    for _ in range(30):
        try:
            urllib.request.urlopen(f"{SERVER_URL}/login/", timeout=1)
            break
        except Exception:
            time.sleep(0.5)
    else:
        proc.kill()
        raise RuntimeError("Django server did not start in time")

    yield proc

    # Teardown
    os.kill(proc.pid, signal.SIGTERM)
    proc.wait(timeout=10)


# Override pytest-playwright's base_url fixture at session scope
@pytest.fixture(scope="session")
def base_url(django_server):
    """Provide base URL — session-scoped to match pytest-base-url expectations."""
    return SERVER_URL


# ---------------------------------------------------------------------------
# Per-test: fresh browser page
# ---------------------------------------------------------------------------
@pytest.fixture()
def page(browser, base_url):
    """A fresh browser page for each test."""
    ctx = browser.new_context(base_url=base_url)
    pg = ctx.new_page()
    yield pg
    pg.close()
    ctx.close()


@pytest.fixture()
def logged_in_page(page, base_url):
    """A page that is already logged in as the superuser (admin)."""
    page.goto(f"{base_url}/login/")
    page.fill("#email", SUPERUSER_EMAIL)
    page.fill("#password", SUPERUSER_PASSWORD)
    with page.expect_navigation():
        page.click("button[type='submit']")
    assert "/dashboard/" in page.url, f"Login failed, ended up at {page.url}"
    return page
