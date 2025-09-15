from retrack.utils.registry import Registry
from retrack.validators.base import BaseValidator
from retrack.validators.check_is_dag import CheckIsDAG
from retrack.validators.node_exists import NodeExistsValidator
from retrack.validators.node_validator import IntervalCatV0Validator


def registry() -> Registry:
    _registry = Registry()
    _registry.register(
        "single_start_node_exists",
        NodeExistsValidator("start", min_quantity=1, max_quantity=1),
    )
    _registry.register("check_is_dag", CheckIsDAG())
    _registry.register("interval_cat_v0", IntervalCatV0Validator())
    return _registry


__all__ = ["registry", "BaseValidator"]
