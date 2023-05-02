from retrack.utils.registry import Registry
from retrack.validators.base import BaseValidator
from retrack.validators.check_is_dag import CheckIsDAG
from retrack.validators.node_exists import NodeExistsValidator

_registry = Registry()


def registry() -> Registry:
    return _registry


def register(name: str, validator: BaseValidator) -> None:
    registry().register(name, validator)


register(
    "single_start_node_exists",
    NodeExistsValidator("start", min_quantity=1, max_quantity=1),
)
register("check_is_dag", CheckIsDAG())


__all__ = ["registry", "register", "BaseValidator"]
