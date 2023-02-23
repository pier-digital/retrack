from retrack.engine.validators.base import BaseValidator
from retrack.engine.validators.node_exists import NodeExistsValidator
from retrack.utils.registry import Registry

registry = Registry()

registry.register(
    "single_start_node_exists",
    NodeExistsValidator("start", min_quantity=1, max_quantity=1),
)

__all__ = ["registry", "BaseValidator"]
