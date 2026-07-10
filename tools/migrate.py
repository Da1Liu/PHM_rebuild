from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "db" / "migrations"


def discover(directory: Path = MIGRATIONS) -> list[Path]:
    return sorted(path for path in directory.glob("[0-9][0-9][0-9][0-9]_*.sql") if path.is_file())


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def applied_migrations(connection: Any) -> dict[str, str]:
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass('phm.schema_migration')")
        if cursor.fetchone()[0] is None:
            connection.rollback()
            return {}
        cursor.execute("SELECT version, checksum_sha256 FROM phm.schema_migration")
        rows = cursor.fetchall()
    connection.rollback()
    return dict(rows)


def migrate(connect: Callable[[], Any], directory: Path = MIGRATIONS) -> list[str]:
    connection = connect()
    applied_now: list[str] = []
    try:
        known = applied_migrations(connection)
        for path in discover(directory):
            version = path.stem
            digest = checksum(path)
            if version in known:
                if known[version] != digest:
                    raise RuntimeError(f"applied migration changed: {version}")
                continue
            with connection.cursor() as cursor:
                cursor.execute(path.read_text("utf-8"))
                cursor.execute(
                    "INSERT INTO phm.schema_migration(version, checksum_sha256) VALUES (%s, %s)",
                    (version, digest),
                )
            connection.commit()
            applied_now.append(version)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    return applied_now


def default_connect(dsn: str):
    try:
        import psycopg
        return lambda: psycopg.connect(dsn)
    except ImportError:
        try:
            import psycopg2
            return lambda: psycopg2.connect(dsn)
        except ImportError as exc:
            raise RuntimeError("install the postgres extra: pip install -e '.[postgres]'") from exc


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply PHM database migrations")
    parser.add_argument("--database-url", default=os.getenv("PHM_DATABASE_URL"))
    args = parser.parse_args()
    if not args.database_url:
        parser.error("--database-url or PHM_DATABASE_URL is required")
    applied = migrate(default_connect(args.database_url))
    print("applied=" + (",".join(applied) if applied else "none"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

