"""Prediction framework foundations."""

from backend.app.prediction.adapters import (
    AshtakavargaAdapter,
    DashaAdapter,
    HouseAnalyzerAdapter,
    LagnaAdapter,
    PlanetAnalyzerAdapter,
    StrengthAdapter,
    YogaAdapter,
)
from backend.app.prediction.conditions import (
    CONDITION_OPERATORS,
    ConditionEvaluation,
    evaluate_all,
    evaluate_any,
    evaluate_condition,
)
from backend.app.prediction.composer import compose_predictions
from backend.app.prediction.categories import (
    discover_rule_categories,
    evaluate_prediction_categories,
    load_prediction_categories,
)
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
from backend.app.prediction.schema import (
    PredictionRule,
    PredictionRuleModel,
    validate_category,
    validate_priority,
    validate_rule,
    validate_rule_id,
)
from backend.app.prediction.registry import (
    clear_rule_registry,
    get_registered_rules,
    register_rule,
    register_rules,
)
from backend.app.prediction.loader import (
    RuleLoaderError,
    load_rule,
    load_rules,
    load_rules_from_yaml,
)

__all__ = [
    "CONDITION_OPERATORS",
    "PREDICTION_STATUSES",
    "AshtakavargaAdapter",
    "ConditionEvaluation",
    "DashaAdapter",
    "HouseAnalyzerAdapter",
    "LagnaAdapter",
    "PlanetAnalyzerAdapter",
    "PredictionResult",
    "PredictionRule",
    "PredictionRuleModel",
    "PredictionStatus",
    "PredictionFrameworkOutput",
    "RuleEvaluationResult",
    "RuleLoaderError",
    "StrengthAdapter",
    "YogaAdapter",
    "build_prediction_context",
    "build_prediction_framework_output",
    "clear_rule_registry",
    "compose_predictions",
    "discover_rule_categories",
    "evaluate_all",
    "evaluate_any",
    "evaluate_condition",
    "evaluate_prediction_categories",
    "evaluate_prediction_rules",
    "evaluate_rule",
    "evaluate_rules",
    "create_empty_prediction_result",
    "create_prediction_result",
    "get_registered_rules",
    "load_prediction_categories",
    "load_rule",
    "load_rules",
    "load_rules_from_yaml",
    "register_rule",
    "register_rules",
    "sort_rules_by_priority",
    "validate_category",
    "validate_priority",
    "validate_rule",
    "validate_rule_id",
]
