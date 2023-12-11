import json
import typing

from retrack import nodes
from retrack.engine.rule import Rule, RuleExecutor
from retrack.utils import registry


def from_json(
    graph_data: typing.Union[str, dict],
    name: str = None,
    nodes_registry: registry.Registry = nodes.registry(),
    dynamic_nodes_registry: registry.Registry = nodes.dynamic_nodes_registry(),
    return_executor: bool = True,
    **kwargs,
) -> typing.Union[Rule, RuleExecutor]:
    """Create a rule from a json file or a dict.

    Args:
        graph_data (typing.Union[str, dict]): Graph data.
        name (str, optional): Rule name. Defaults to None.
        nodes_registry (registry.Registry, optional): Nodes registry. Defaults to nodes.registry().
        dynamic_nodes_registry (registry.Registry, optional): Dynamic nodes registry. Defaults to nodes.dynamic_nodes_registry().
        return_executor (bool, optional): Whether to return the executor or the rule. Defaults to True.

    Raises:
        ValueError: If the data is not a dict or a json file path.

    Returns:
        typing.Union[Rule, RuleExecutor]: Rule or RuleExecutor depending on return_executor.
    """
    if isinstance(graph_data, str) and graph_data.endswith(".json"):
        if name is None:
            name = graph_data
        graph_data = json.loads(open(graph_data).read())
    elif not isinstance(graph_data, dict):
        raise ValueError("data must be a dict or a json file path")

    rule = Rule.create(
        graph_data=graph_data,
        name=name,
        nodes_registry=nodes_registry,
        dynamic_nodes_registry=dynamic_nodes_registry,
        **kwargs,
    )
    return rule.executor if return_executor else rule
