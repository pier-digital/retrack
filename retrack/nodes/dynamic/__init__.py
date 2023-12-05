import typing

from retrack.nodes.dynamic.base import BaseDynamicNode
from retrack.nodes.dynamic.csv_table import csv_table_factory
from retrack.nodes.dynamic.flow import flow_factory
from retrack.utils.registry import Registry


def registry() -> Registry:
    _registry = Registry()

    _registry.register("CSVTableV0", csv_table_factory)
    _registry.register("FlowV0", flow_factory)

    return _registry


__all__ = ["registry", "BaseDynamicNode"]
