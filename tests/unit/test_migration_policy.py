from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_runtime_source_does_not_create_tables() -> None:
    runtime_roots = [ROOT / "apps", ROOT / "agents", ROOT / "packages"]
    offenders = []
    for root in runtime_roots:
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".py", ".js", ".ts", ".cs", ".sql"}:
                if "CREATE TABLE" in path.read_text("utf-8", errors="ignore").upper():
                    offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []

