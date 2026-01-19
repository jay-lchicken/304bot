import asyncio
from urllib.parse import urlparse


def _connect_postgres(database_url: str):
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError(
            "psycopg is not installed. Run `pip install psycopg[binary]`."
        ) from exc

    return psycopg.connect(database_url)


def _validate_database_url(database_url: str) -> None:
    scheme = urlparse(database_url).scheme.lower()
    if scheme not in ("postgres", "postgresql"):
        raise ValueError(f"Unsupported DATABASE_URL scheme '{scheme}'. Use postgres.")


def _insert_connection_row(
    database_url: str,
    username: str,
    met_name: str,
    details: str | None,
) -> None:
    _validate_database_url(database_url)
    conn = _connect_postgres(database_url)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO connections (username, met_name, details) VALUES (%s, %s, %s);",
                (username, met_name, details),
            )
            cur.close()
    finally:
        conn.close()


def _fetch_connection_rows(database_url: str):
    _validate_database_url(database_url)
    conn = _connect_postgres(database_url)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT username, met_name, details, date_added "
                "FROM connections ORDER BY date_added DESC;"
            )
            rows = cur.fetchall()
            cur.close()
            return rows
    finally:
        conn.close()


def _fetch_distinct_usernames_between(database_url: str, start_dt, end_dt):
    _validate_database_url(database_url)
    conn = _connect_postgres(database_url)
    try:
        with conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT DISTINCT username FROM connections "
                "WHERE date_added >= %s AND date_added < %s;",
                (start_dt, end_dt),
            )
            rows = cur.fetchall()
            cur.close()
            return {row[0] for row in rows}
    finally:
        conn.close()


async def insert_connection_row(
    database_url: str,
    username: str,
    met_name: str,
    details: str | None,
) -> None:
    await asyncio.to_thread(
        _insert_connection_row,
        database_url,
        username,
        met_name,
        details,
    )


async def fetch_connection_rows(database_url: str):
    return await asyncio.to_thread(_fetch_connection_rows, database_url)


async def fetch_distinct_usernames_between(database_url: str, start_dt, end_dt):
    return await asyncio.to_thread(
        _fetch_distinct_usernames_between,
        database_url,
        start_dt,
        end_dt,
    )
