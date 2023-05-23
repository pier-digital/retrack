import typing

from retrack.nodes.dynamic.base import BaseDynamicNode
from retrack.nodes.dynamic.csv_table import csv_table_factory
from retrack.utils.registry import Registry

_registry = Registry()


def registry() -> Registry:
    return _registry


def register(
    name: str,
    factory: typing.Callable[
        [typing.List[str], typing.List[str]], typing.Type[BaseDynamicNode]
    ],
) -> None:
    registry().register(name, factory)


register("CSVTable", csv_table_factory)

__all__ = ["registry", "register", "BaseDynamicNode"]