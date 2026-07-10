from datetime import datetime, timezone

from phm_application.ports import EvaluationRecord
from phm_domain import EvaluationState
from phm_persistence import PostgresEvaluationRepository


class FakeCursor:
    def __init__(self, rows):
        self.rows = iter(rows)
        self.executions = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def execute(self, query, params):
        self.executions.append((" ".join(query.split()), params))

    def fetchone(self):
        return next(self.rows)


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def cursor(self):
        return self._cursor


def row(record):
    return (
        record.evaluation_id, record.window_id, record.baseline_id, record.state.value,
        record.evaluated_at, record.score, record.t2, record.spe, record.ucl_t2,
        record.ucl_spe, list(record.evidence), record.reason,
    )


def test_add_uses_database_idempotency_key() -> None:
    record = EvaluationRecord(
        evaluation_id="11111111-1111-1111-1111-111111111111",
        window_id="window-1", baseline_id=None,
        state=EvaluationState.INSUFFICIENT_DATA,
        evaluated_at=datetime(2026, 7, 10, tzinfo=timezone.utc),
    )
    cursor = FakeCursor([row(record)])
    repository = PostgresEvaluationRepository(lambda: FakeConnection(cursor))
    saved = repository.add(record)
    assert saved == record
    assert "ON CONFLICT (window_id, baseline_identity) DO NOTHING" in cursor.executions[0][0]

