"""Test database bootstrap.

The test database is no longer committed to the repository. Instead it is
built fresh from the test migrations and seeds at the start of every test
session, so the suite always starts from a known, clean state and nothing has
to be restored afterwards.
"""
import os

import pytest

# Importing the test database config registers the sqlite connection details
# with the ORM's ConnectionResolver.
from tests.integrations.config.database import DATABASES

MIGRATION_DIRECTORY = "tests/integrations/databases/migrations"
DATABASE_FILE = DATABASES["sqlite"]["database"]


@pytest.fixture(scope="session", autouse=True)
def build_test_database():
    """Create the sqlite test database from migrations + seeds once per session."""
    from masoniteorm.migrations import Migration

    # Start from a clean slate so the schema and seed data are deterministic.
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
    os.makedirs(os.path.dirname(DATABASE_FILE), exist_ok=True)

    migration = Migration(
        connection="sqlite", migration_directory=MIGRATION_DIRECTORY
    )
    migration.create_table_if_not_exists()
    migration.migrate()

    from tests.integrations.databases.seeds.database_seeder import DatabaseSeeder

    DatabaseSeeder().run()

    yield
