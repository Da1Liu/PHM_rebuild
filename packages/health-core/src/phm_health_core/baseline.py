from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from phm_domain import EvaluationState


class ModelNotFittedError(RuntimeError):
    pass


@dataclass(frozen=True)
class Evaluation:
    state: EvaluationState
    score: float | None
    t2: float | None
    spe: float | None
    ucl_t2: float | None
    ucl_spe: float | None
    contributions: tuple[dict[str, float | str], ...] = ()
    reason: str | None = None


class BaselineModel:
    """无外部状态依赖的 PCA T²/SPE 基线模型。"""

    def __init__(self, feature_names: Sequence[str], *, variance_to_keep: float = 0.95,
                 control_quantile: float = 0.99, minimum_samples: int | None = None) -> None:
        names = tuple(feature_names)
        if not names or len(set(names)) != len(names):
            raise ValueError("feature_names must be non-empty and unique")
        if not 0 < variance_to_keep <= 1:
            raise ValueError("variance_to_keep must be in (0, 1]")
        if not 0 < control_quantile < 1:
            raise ValueError("control_quantile must be in (0, 1)")
        self.feature_names = names
        self.variance_to_keep = variance_to_keep
        self.control_quantile = control_quantile
        self.minimum_samples = minimum_samples or max(10, 2 * len(names))
        self.mean_: np.ndarray | None = None
        self.scale_: np.ndarray | None = None
        self.components_: np.ndarray | None = None
        self.eigenvalues_: np.ndarray | None = None
        self.ucl_t2_: float | None = None
        self.ucl_spe_: float | None = None
        self.n_samples_ = 0

    @property
    def fitted(self) -> bool:
        return self.mean_ is not None

    def fit(self, train: np.ndarray, calibration: np.ndarray | None = None) -> "BaselineModel":
        x = self._matrix(train)
        if len(x) < self.minimum_samples:
            raise ValueError(f"insufficient baseline samples: {len(x)} < {self.minimum_samples}")
        self.mean_ = x.mean(axis=0)
        raw_scale = x.std(axis=0)
        if np.any(raw_scale <= 1e-12):
            invalid = [self.feature_names[i] for i in np.flatnonzero(raw_scale <= 1e-12)]
            raise ValueError(f"constant baseline features: {', '.join(invalid)}")
        self.scale_ = raw_scale
        z = (x - self.mean_) / self.scale_
        _, singular_values, vt = np.linalg.svd(z, full_matrices=False)
        eigenvalues = singular_values ** 2 / max(len(z) - 1, 1)
        ratios = eigenvalues / eigenvalues.sum()
        count = int(np.searchsorted(np.cumsum(ratios), self.variance_to_keep) + 1)
        count = min(max(count, 1), x.shape[1])
        self.components_ = vt[:count].T
        self.eigenvalues_ = np.maximum(eigenvalues[:count], 1e-12)
        self.n_samples_ = len(x)
        limits_source = x if calibration is None else self._matrix(calibration)
        if len(limits_source) < 5:
            raise ValueError("calibration requires at least 5 samples")
        t2, spe = self._statistics(limits_source)
        self.ucl_t2_ = float(max(np.quantile(t2, self.control_quantile), 1e-12))
        self.ucl_spe_ = float(max(np.quantile(spe, self.control_quantile), 1e-12))
        return self

    def evaluate(self, sample: np.ndarray) -> Evaluation:
        if not self.fitted:
            return Evaluation(EvaluationState.INSUFFICIENT_DATA, None, None, None, None, None,
                              reason="baseline_not_fitted")
        try:
            x = self._matrix(sample)
        except ValueError as exc:
            return Evaluation(EvaluationState.INVALID_DATA, None, None, None,
                              self.ucl_t2_, self.ucl_spe_, reason=str(exc))
        if len(x) != 1:
            raise ValueError("evaluate accepts exactly one sample")
        z = (x[0] - self.mean_) / self.scale_
        projection = self.components_.T @ z
        residual = z - self.components_ @ projection
        t2 = float(np.sum(projection ** 2 / self.eigenvalues_))
        spe = float(np.sum(residual ** 2))
        score = max(t2 / self.ucl_t2_, spe / self.ucl_spe_)
        t2_contrib = z * (self.components_ @ (projection / self.eigenvalues_))
        contributions = tuple(
            {"name": name, "t2": float(tc), "spe": float(sc)}
            for name, tc, sc in zip(self.feature_names, t2_contrib, residual ** 2)
        )
        state = EvaluationState.DEVIATING if score > 1 else EvaluationState.NORMAL
        return Evaluation(state, float(score), t2, spe, self.ucl_t2_, self.ucl_spe_, contributions)

    def to_dict(self) -> dict[str, object]:
        if not self.fitted:
            raise ModelNotFittedError("cannot serialize an unfitted model")
        return {"modelType": "pca-t2-spe", "modelVersion": "1.0",
                "featureNames": list(self.feature_names), "varianceToKeep": self.variance_to_keep,
                "controlQuantile": self.control_quantile, "minimumSamples": self.minimum_samples,
                "mean": self.mean_.tolist(), "scale": self.scale_.tolist(),
                "components": self.components_.tolist(), "eigenvalues": self.eigenvalues_.tolist(),
                "uclT2": self.ucl_t2_, "uclSpe": self.ucl_spe_, "sampleCount": self.n_samples_}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "BaselineModel":
        if payload.get("modelType") != "pca-t2-spe" or payload.get("modelVersion") != "1.0":
            raise ValueError("unsupported model type or version")
        model = cls(payload["featureNames"], variance_to_keep=float(payload["varianceToKeep"]),
                    control_quantile=float(payload["controlQuantile"]),
                    minimum_samples=int(payload["minimumSamples"]))
        model.mean_ = np.asarray(payload["mean"], dtype=float)
        model.scale_ = np.asarray(payload["scale"], dtype=float)
        model.components_ = np.asarray(payload["components"], dtype=float)
        model.eigenvalues_ = np.asarray(payload["eigenvalues"], dtype=float)
        model.ucl_t2_ = float(payload["uclT2"])
        model.ucl_spe_ = float(payload["uclSpe"])
        model.n_samples_ = int(payload["sampleCount"])
        return model

    def _matrix(self, values: np.ndarray) -> np.ndarray:
        x = np.atleast_2d(np.asarray(values, dtype=float))
        if x.ndim != 2 or x.shape[1] != len(self.feature_names):
            raise ValueError(f"expected {len(self.feature_names)} features")
        if not np.all(np.isfinite(x)):
            raise ValueError("features must be finite")
        return x

    def _statistics(self, values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        z = (values - self.mean_) / self.scale_
        projection = z @ self.components_
        t2 = np.sum(projection ** 2 / self.eigenvalues_, axis=1)
        residual = z - projection @ self.components_.T
        return t2, np.sum(residual ** 2, axis=1)

