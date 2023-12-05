from retrack.utils.registry import Registry
from retrack.validators.base import BaseValidator
from retrack.validators.check_is_dag import CheckIsDAG
from retrack.validators.node_exists import NodeExistsValidator


def registry() -> Registry:
    _registry = Registry()
    _registry.register(
        "single_start_node_exists",
        NodeExistsValidator("start", min_quantity=1, max_quantity=1),
    )
    _registry.register("check_is_dag", CheckIsDAG())
    return _registry


__all__ = ["registry", "BaseValidator"]
