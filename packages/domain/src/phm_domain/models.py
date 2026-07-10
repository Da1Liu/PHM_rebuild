from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Mapping


class MeasurementQuality(str, Enum):
    GOOD = "good"
    UNCERTAIN = "uncertain"
    BAD = "bad"
    MISSING = "missing"


class EvaluationState(str, Enum):
    NOT_EVALUABLE = "not_evaluable"
    INSUFFICIENT_DATA = "insufficient_data"
    NORMAL = "normal"
    DEVIATING = "deviating"
    INVALID_DATA = "invalid_data"


def _require_aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


@dataclass(frozen=True)
class ScalarObservation:
    message_id: str
    machine_id: str
    signal_code: str
    observed_at: datetime
    received_at: datetime
    value: float | None
    quality: MeasurementQuality
    context: Mapping[str, str | int | float | bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _require_aware(self.observed_at, "observed_at")
        _require_aware(self.received_at, "received_at")
        if not self.message_id or not self.machine_id or not self.signal_code:
            raise ValueError("message_id, machine_id and signal_code are required")
        if self.quality is MeasurementQuality.GOOD:
            if self.value is None or not isfinite(self.value):
                raise ValueError("good observations require a finite value")


@dataclass(frozen=True)
class FeatureWindow:
    window_id: str
    machine_id: str
    source_signal_codes: tuple[str, ...]
    window_start: datetime
    window_end: datetime
    received_at: datetime
    features: Mapping[str, float]
    quality: MeasurementQuality
    context: Mapping[str, str | int | float | bool] = field(default_factory=dict)
    epoch: int = 1

    def __post_init__(self) -> None:
        for name, value in (
            ("window_start", self.window_start),
            ("window_end", self.window_end),
            ("received_at", self.received_at),
        ):
            _require_aware(value, name)
        if self.window_end <= self.window_start:
            raise ValueError("window_end must be after window_start")
        if self.epoch < 1:
            raise ValueError("epoch must be positive")
        if self.quality is MeasurementQuality.GOOD:
            if not self.features or any(not isfinite(v) for v in self.features.values()):
                raise ValueError("good feature windows require finite features")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

