import json
import typing

from retrack import nodes
from retrack.engine.rule import Rule, RuleExecutor
from retrack.utils import registry


def from_json(
    data: typing.Union[str, dict],
    name: str = None,
    nodes_registry: registry.Registry = nodes.registry(),
    dynamic_nodes_registry: registry.Registry = nodes.dynamic_nodes_registry(),
    **kwargs,
) -> RuleExecutor:
    """Create a Rule Executor from a json file or a dict.

    Args:
        data (typing.Union[str, dict]): json file path or a dict.
        name (str, optional): Rule name. Defaults to None.
        nodes_registry (registry.Registry, optional): Nodes registry. Defaults to nodes.registry().
        dynamic_nodes_registry (registry.Registry, optional): Dynamic nodes registry. Defaults to nodes.dynamic_nodes_registry().

    Raises:
        ValueError: If data is not a dict or a json file path.

    Returns:
        RuleExecutor: Rule executor.
    """
    if isinstance(data, str) and data.endswith(".json"):
        if name is None:
            name = data
        graph_data = json.loads(open(data).read())
    elif not isinstance(data, dict):
        raise ValueError("data must be a dict or a json file path")

    rule = Rule.create(
        graph_data=graph_data,
        name=name,
        nodes_registry=nodes_registry,
        dynamic_nodes_registry=dynamic_nodes_registry,
        **kwargs,
    )
    return rule.executor
