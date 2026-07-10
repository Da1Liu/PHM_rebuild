from datetime import datetime, timezone

import pytest

from phm_domain import MeasurementQuality, ScalarObservation


NOW = datetime(2026, 7, 10, tzinfo=timezone.utc)


def test_good_observation_requires_value() -> None:
    with pytest.raises(ValueError):
        ScalarObservation(
            message_id="m1",
            machine_id="machine-01",
            signal_code="speed",
            observed_at=NOW,
            received_at=NOW,
            value=None,
            quality=MeasurementQuality.GOOD,
        )


def test_missing_observation_does_not_invent_zero() -> None:
    observation = ScalarObservation(
        message_id="m2",
        machine_id="machine-01",
        signal_code="speed",
        observed_at=NOW,
        received_at=NOW,
        value=None,
        quality=MeasurementQuality.MISSING,
    )
    assert observation.value is None

