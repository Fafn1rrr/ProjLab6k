import os

import psycopg


class DatabaseConfigurationError(RuntimeError):
    pass


def get_connection():
    database_url = os.getenv("DATABASE_URL", "").strip()

    if not database_url:
        raise DatabaseConfigurationError(
            "DATABASE_URL is missing or empty"
        )

    return psycopg.connect(
        database_url,
        connect_timeout=10
    )