"""Prediction framework foundations."""

from backend.app.prediction.conditions import (
    CONDITION_OPERATORS,
    ConditionEvaluation,
    evaluate_all,
    evaluate_any,
    evaluate_condition,
)
from backend.app.prediction.composer import compose_predictions
from backend.app.prediction.framework import (
    PredictionFrameworkOutput,
    build_prediction_context,
    build_prediction_framework_output,
    evaluate_prediction_rules,
)
from backend.app.prediction.result import (
    PREDICTION_STATUSES,
    PredictionResult,
    PredictionStatus,
    create_empty_prediction_result,
    create_prediction_result,
)

__all__ = [
    "CONDITION_OPERATORS",
    "PREDICTION_STATUSES",
    "ConditionEvaluation",
    "PredictionResult",
    "PredictionStatus",
    "PredictionFrameworkOutput",
    "build_prediction_context",
    "build_prediction_framework_output",
    "compose_predictions",
    "evaluate_all",
    "evaluate_any",
    "evaluate_condition",
    "evaluate_prediction_rules",
    "create_empty_prediction_result",
    "create_prediction_result",
]
