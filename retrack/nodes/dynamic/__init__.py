from retrack.nodes.dynamic.base import BaseDynamicNode
from retrack.nodes.dynamic.csv_table import csv_table_factory
from retrack.nodes.dynamic.flow import flow_factory
from retrack.nodes.dynamic.conditional_connector import conditional_connector_factory
from retrack.nodes.dynamic.glm import glm_factory
from retrack.utils.registry import Registry


def registry() -> Registry:
    """Create a registry with all the dynamic nodes available in the library.

    A dynamic node is a node that is not explicitly defined in the nodes registry, but is created dynamically from a factory function."""
    _registry = Registry()

    _registry.register("CSVTableV0", csv_table_factory)
    _registry.register("FlowV0", flow_factory)
    _registry.register("ConditionalConnector", conditional_connector_factory)
    _registry.register("BureauConnector", conditional_connector_factory)
    _registry.register("ModelConnector", conditional_connector_factory)
    _registry.register("FeatureConnector", conditional_connector_factory)
    _registry.register("GLM", glm_factory)

    return _registry


__all__ = ["registry", "BaseDynamicNode"]
