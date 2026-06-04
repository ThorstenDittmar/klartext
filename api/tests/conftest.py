"""Pytest configuration for the klartext test suite.

Loads environment variables from api/.env before integration tests run,
so SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are available without
having to export them manually in the shell.
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

# Load api/.env — relative to this conftest, two levels up is the api/ directory
_ENV_FILE = Path(__file__).parent.parent / ".env"
load_dotenv(_ENV_FILE, override=False)
