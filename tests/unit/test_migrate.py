from pathlib import Path

import pytest

from tools.migrate import checksum, discover


def test_discover_orders_numbered_sql_files(tmp_path: Path) -> None:
    (tmp_path / "0002_second.sql").write_text("select 2", "utf-8")
    (tmp_path / "notes.sql").write_text("ignored", "utf-8")
    (tmp_path / "0001_first.sql").write_text("select 1", "utf-8")
    assert [path.name for path in discover(tmp_path)] == ["0001_first.sql", "0002_second.sql"]


def test_checksum_changes_with_content(tmp_path: Path) -> None:
    path = tmp_path / "0001_test.sql"
    path.write_text("select 1", "utf-8")
    before = checksum(path)
    path.write_text("select 2", "utf-8")
    assert checksum(path) != before

