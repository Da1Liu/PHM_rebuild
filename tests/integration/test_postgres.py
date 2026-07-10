from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from phm_application import EvaluationService
from phm_domain import FeatureWindow, MeasurementQuality
from phm_persistence import PostgresEvaluationRepository


DSN = os.getenv("PHM_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DSN, reason="PHM_TEST_DATABASE_URL is not configured")


def connect():
    try:
        import psycopg
        return psycopg.connect(DSN)
    except ImportError:
        import psycopg2
        return psycopg2.connect(DSN)


def test_evaluation_repository_is_idempotent_against_postgres() -> None:
    suffix = uuid4().hex
    machine_id = f"test-machine-{suffix}"
    window_id = f"test-window-{suffix}"
    connection = connect()
    try:
        now = datetime.now(timezone.utc)
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO phm.machine(machine_id, display_name) VALUES (%s, %s)",
                (machine_id, "Temporary integration machine"),
            )
            cursor.execute(
                """INSERT INTO phm.feature_window
                   (window_id, machine_id, epoch, window_start, window_end, received_at,
                    source_signal_ids, features, quality)
                   VALUES (%s, %s, 1, %s, %s, %s, %s, %s::jsonb, 'good')""",
                (window_id, machine_id, now, now + timedelta(seconds=1), now, [1], '{"rms":0.1}'),
            )
        connection.commit()

        window = FeatureWindow(
            window_id, machine_id, ("vib-1",), now, now + timedelta(seconds=1), now,
            {"rms": 0.1}, MeasurementQuality.GOOD,
        )
        service = EvaluationService(PostgresEvaluationRepository(connect))
        first = service.evaluate(window, None, None)
        second = service.evaluate(window, None, None)
        assert first.created is True
        assert second.created is False
        assert first.record.evaluation_id == second.record.evaluation_id
    finally:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM phm.evaluation_result WHERE window_id=%s", (window_id,))
            cursor.execute("DELETE FROM phm.feature_window WHERE window_id=%s", (window_id,))
            cursor.execute("DELETE FROM phm.machine WHERE machine_id=%s", (machine_id,))
        connection.commit()
        connection.close()

