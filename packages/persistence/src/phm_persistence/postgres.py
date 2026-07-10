from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Callable

from phm_application.ports import EvaluationRecord
from phm_domain import EvaluationState


class PostgresEvaluationRepository:
    """依赖 PEP 249 风格 connection factory，不在模块导入时绑定具体驱动。"""

    def __init__(self, connect: Callable[[], Any]) -> None:
        self._connect = connect

    def find(self, window_id: str, baseline_id: str | None) -> EvaluationRecord | None:
        query = """
            SELECT evaluation_id::text, window_id, baseline_id::text, state,
                   evaluated_at, score, t2, spe, ucl_t2, ucl_spe, evidence, reason
              FROM phm.evaluation_result
             WHERE window_id = %s AND baseline_id IS NOT DISTINCT FROM %s::uuid
        """
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(query, (window_id, baseline_id))
            row = cursor.fetchone()
        return None if row is None else self._record(row)

    def add(self, record: EvaluationRecord) -> EvaluationRecord:
        query = """
            INSERT INTO phm.evaluation_result
                (evaluation_id, window_id, baseline_id, state, evaluated_at,
                 score, t2, spe, ucl_t2, ucl_spe, evidence, reason)
            VALUES (%s::uuid, %s, %s::uuid, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
            ON CONFLICT (window_id, baseline_identity) DO NOTHING
            RETURNING evaluation_id::text, window_id, baseline_id::text, state,
                      evaluated_at, score, t2, spe, ucl_t2, ucl_spe, evidence, reason
        """
        values = (
            record.evaluation_id, record.window_id, record.baseline_id, record.state.value,
            record.evaluated_at, record.score, record.t2, record.spe, record.ucl_t2,
            record.ucl_spe, json.dumps(record.evidence), record.reason,
        )
        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(query, values)
            row = cursor.fetchone()
            if row is None:
                cursor.execute(
                    """SELECT evaluation_id::text, window_id, baseline_id::text, state,
                              evaluated_at, score, t2, spe, ucl_t2, ucl_spe, evidence, reason
                         FROM phm.evaluation_result
                        WHERE window_id=%s AND baseline_id IS NOT DISTINCT FROM %s::uuid""",
                    (record.window_id, record.baseline_id),
                )
                row = cursor.fetchone()
        return self._record(row)

    @staticmethod
    def _record(row: tuple[Any, ...]) -> EvaluationRecord:
        evidence = row[10]
        if isinstance(evidence, str):
            evidence = json.loads(evidence)
        return EvaluationRecord(
            evaluation_id=row[0], window_id=row[1], baseline_id=row[2],
            state=EvaluationState(row[3]), evaluated_at=row[4], score=row[5],
            t2=row[6], spe=row[7], ucl_t2=row[8], ucl_spe=row[9],
            evidence=tuple(evidence or ()), reason=row[11],
        )

