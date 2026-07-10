from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

import numpy as np

from phm_domain import EvaluationState, FeatureWindow, MeasurementQuality
from phm_health_core import BaselineModel

from .ports import EvaluationRecord, EvaluationRepository


@dataclass(frozen=True)
class EvaluationSummary:
    record: EvaluationRecord
    created: bool


class EvaluationService:
    """将领域窗口交给纯算法内核，并保证相同窗口/模型只产生一条结果。"""

    def __init__(self, repository: EvaluationRepository) -> None:
        self._repository = repository

    def evaluate(self, window: FeatureWindow, baseline_id: str | None,
                 model: BaselineModel | None) -> EvaluationSummary:
        existing = self._repository.find(window.window_id, baseline_id)
        if existing is not None:
            return EvaluationSummary(existing, created=False)

        now = datetime.now(timezone.utc)
        if window.quality is not MeasurementQuality.GOOD:
            record = EvaluationRecord(
                evaluation_id=str(uuid4()), window_id=window.window_id,
                baseline_id=baseline_id, state=EvaluationState.NOT_EVALUABLE,
                evaluated_at=now, reason=f"window_quality:{window.quality.value}",
            )
        elif model is None:
            record = EvaluationRecord(
                evaluation_id=str(uuid4()), window_id=window.window_id,
                baseline_id=None, state=EvaluationState.INSUFFICIENT_DATA,
                evaluated_at=now, reason="active_baseline_not_found",
            )
        else:
            missing = [name for name in model.feature_names if name not in window.features]
            extras = [name for name in window.features if name not in model.feature_names]
            if missing or extras:
                detail = f"feature_schema_mismatch:missing={missing},extras={extras}"
                record = EvaluationRecord(
                    evaluation_id=str(uuid4()), window_id=window.window_id,
                    baseline_id=baseline_id, state=EvaluationState.INVALID_DATA,
                    evaluated_at=now, reason=detail,
                )
            else:
                vector = np.array([window.features[name] for name in model.feature_names])
                result = model.evaluate(vector)
                record = EvaluationRecord(
                    evaluation_id=str(uuid4()), window_id=window.window_id,
                    baseline_id=baseline_id, state=result.state, evaluated_at=now,
                    score=result.score, t2=result.t2, spe=result.spe,
                    ucl_t2=result.ucl_t2, ucl_spe=result.ucl_spe,
                    evidence=result.contributions, reason=result.reason,
                )
        return EvaluationSummary(self._repository.add(record), created=True)

