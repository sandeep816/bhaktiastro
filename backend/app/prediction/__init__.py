"""Prediction framework foundations."""

from backend.app.prediction.result import (
    PREDICTION_STATUSES,
    PredictionResult,
    PredictionStatus,
    create_empty_prediction_result,
    create_prediction_result,
)

__all__ = [
    "PREDICTION_STATUSES",
    "PredictionResult",
    "PredictionStatus",
    "create_empty_prediction_result",
    "create_prediction_result",
]
