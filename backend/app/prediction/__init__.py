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
from backend.app.prediction.rules import (
    RuleEvaluationResult,
    evaluate_rule,
    evaluate_rules,
    sort_rules_by_priority,
)

__all__ = [
    "CONDITION_OPERATORS",
    "PREDICTION_STATUSES",
    "ConditionEvaluation",
    "PredictionResult",
    "PredictionStatus",
    "PredictionFrameworkOutput",
    "RuleEvaluationResult",
    "build_prediction_context",
    "build_prediction_framework_output",
    "compose_predictions",
    "evaluate_all",
    "evaluate_any",
    "evaluate_condition",
    "evaluate_prediction_rules",
    "evaluate_rule",
    "evaluate_rules",
    "create_empty_prediction_result",
    "create_prediction_result",
    "sort_rules_by_priority",
]
