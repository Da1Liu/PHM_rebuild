from __future__ import annotations

from .ports import EvaluationRecord


class MemoryEvaluationRepository:
    def __init__(self) -> None:
        self._records: dict[tuple[str, str | None], EvaluationRecord] = {}

    def find(self, window_id: str, baseline_id: str | None) -> EvaluationRecord | None:
        return self._records.get((window_id, baseline_id))

    def add(self, record: EvaluationRecord) -> EvaluationRecord:
        key = (record.window_id, record.baseline_id)
        existing = self._records.get(key)
        if existing is not None:
            return existing
        self._records[key] = record
        return record

