from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from phm_domain import EvaluationState


@dataclass(frozen=True)
class EvaluationRecord:
    evaluation_id: str
    window_id: str
    baseline_id: str | None
    state: EvaluationState
    evaluated_at: datetime
    score: float | None = None
    t2: float | None = None
    spe: float | None = None
    ucl_t2: float | None = None
    ucl_spe: float | None = None
    evidence: tuple[dict[str, float | str], ...] = ()
    reason: str | None = None


class EvaluationRepository(Protocol):
    def find(self, window_id: str, baseline_id: str | None) -> EvaluationRecord | None: ...

    def add(self, record: EvaluationRecord) -> EvaluationRecord: ...

