from datetime import datetime, timedelta, timezone

import numpy as np

from phm_application import EvaluationService, MemoryEvaluationRepository
from phm_domain import EvaluationState, FeatureWindow, MeasurementQuality
from phm_health_core import BaselineModel


NOW = datetime(2026, 7, 10, tzinfo=timezone.utc)


def window(features: dict[str, float], quality: MeasurementQuality = MeasurementQuality.GOOD) -> FeatureWindow:
    return FeatureWindow(
        window_id="window-1", machine_id="machine-1", source_signal_codes=("vib-1",),
        window_start=NOW, window_end=NOW + timedelta(seconds=1), received_at=NOW,
        features=features, quality=quality,
    )


def fitted_model() -> BaselineModel:
    rng = np.random.default_rng(2)
    train = rng.normal(size=(60, 2))
    return BaselineModel(["rms", "crest"], minimum_samples=20).fit(train[:50], train[50:])


def test_evaluation_is_idempotent() -> None:
    service = EvaluationService(MemoryEvaluationRepository())
    first = service.evaluate(window({"rms": 0.1, "crest": 0.2}), "baseline-1", fitted_model())
    second = service.evaluate(window({"rms": 99.0, "crest": 99.0}), "baseline-1", fitted_model())
    assert first.created is True
    assert second.created is False
    assert second.record.evaluation_id == first.record.evaluation_id


def test_bad_quality_is_not_evaluable() -> None:
    result = EvaluationService(MemoryEvaluationRepository()).evaluate(
        window({}, MeasurementQuality.BAD), "baseline-1", fitted_model())
    assert result.record.state is EvaluationState.NOT_EVALUABLE
    assert result.record.score is None


def test_missing_baseline_is_insufficient_data() -> None:
    result = EvaluationService(MemoryEvaluationRepository()).evaluate(
        window({"rms": 0.1, "crest": 0.2}), None, None)
    assert result.record.state is EvaluationState.INSUFFICIENT_DATA


def test_feature_schema_mismatch_is_invalid() -> None:
    result = EvaluationService(MemoryEvaluationRepository()).evaluate(
        window({"rms": 0.1, "unexpected": 0.2}), "baseline-1", fitted_model())
    assert result.record.state is EvaluationState.INVALID_DATA
    assert "feature_schema_mismatch" in result.record.reason

