import os
from urllib.parse import urlparse

from dotenv import load_dotenv


def _connect_postgres(database_url: str):
    try:
        import psycopg
    except ImportError as exc:
        raise SystemExit(
            "psycopg is not installed. Run `pip install psycopg[binary]` "
            "or switch DATABASE_URL to a sqlite URL."
        ) from exc

    return psycopg.connect(database_url)


def init_db(database_url: str) -> None:
    scheme = urlparse(database_url).scheme.lower()
    is_postgres = scheme in ("postgres", "postgresql")

    if not is_postgres:
        raise SystemExit(
            f"Unsupported DATABASE_URL scheme '{scheme}'. Use postgres."
        )

    conn = _connect_postgres(database_url)
    create_sql = """
        CREATE TABLE IF NOT EXISTS connections (
            username TEXT NOT NULL,
            met_name TEXT NOT NULL,
            details TEXT,
            date_added TIMESTAMPTZ DEFAULT NOW()
        );
    """
    alter_sql = "ALTER TABLE connections ADD COLUMN IF NOT EXISTS details TEXT;"

    try:
        with conn:
            cur = conn.cursor()
            cur.execute(create_sql)
            cur.execute(alter_sql)
            cur.close()
    finally:
        conn.close()


if __name__ == "__main__":
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is not set.")
    init_db(database_url)
