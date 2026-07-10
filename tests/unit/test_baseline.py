import numpy as np
import pytest

from phm_domain import EvaluationState
from phm_health_core import BaselineModel


def healthy_data(seed: int = 7, count: int = 200) -> np.ndarray:
    rng = np.random.default_rng(seed)
    latent = rng.normal(size=(count, 2))
    noise = rng.normal(scale=0.08, size=(count, 2))
    return np.column_stack((latent[:, 0], 0.8 * latent[:, 0] + noise[:, 0], latent[:, 1] + noise[:, 1]))


def test_unfitted_model_is_not_reported_as_healthy() -> None:
    result = BaselineModel(["a", "b", "c"]).evaluate(np.zeros(3))
    assert result.state is EvaluationState.INSUFFICIENT_DATA
    assert result.score is None


def test_fit_rejects_constant_features() -> None:
    with pytest.raises(ValueError, match="constant baseline features"):
        BaselineModel(["changing", "constant"]).fit(np.column_stack((np.arange(20), np.ones(20))))


def test_relationship_change_is_exposed_by_spe() -> None:
    train = healthy_data()
    model = BaselineModel(["x", "x_related", "y"], minimum_samples=30).fit(train[:150], train[150:])
    result = model.evaluate(np.array([2.0, -2.0, 0.0]))
    assert result.state is EvaluationState.DEVIATING
    assert result.spe > result.ucl_spe


def test_serialization_round_trip_is_stable() -> None:
    train = healthy_data()
    model = BaselineModel(["x", "x_related", "y"], minimum_samples=30).fit(train[:150], train[150:])
    restored = BaselineModel.from_dict(model.to_dict())
    assert restored.evaluate(train[20]).score == pytest.approx(model.evaluate(train[20]).score)


def test_non_finite_sample_is_invalid_data() -> None:
    train = healthy_data()
    model = BaselineModel(["x", "x_related", "y"], minimum_samples=30).fit(train[:150], train[150:])
    result = model.evaluate(np.array([0.0, np.nan, 0.0]))
    assert result.state is EvaluationState.INVALID_DATA
    assert result.score is None

