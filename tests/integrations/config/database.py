from masoniteorm.connections import ConnectionResolver

DATABASES = {
    "default": "sqlite",
    "sqlite": {
        "driver": "sqlite",
        # Built fresh from migrations + seeds at the start of each test session
        # (see tests/conftest.py); never committed.
        "database": "tests/integrations/databases/database.sqlite3",
    },
}

DB = ConnectionResolver().set_connection_details(DATABASES)
