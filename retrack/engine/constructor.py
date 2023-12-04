import typing

import json

from retrack.engine.rule import Rule, RuleExecutor
from retrack.utils import registry
from retrack import nodes


def from_json(
    data: typing.Union[str, dict],
    name: str = None,
    nodes_registry: registry.Registry = nodes.registry(),
    dynamic_nodes_registry: registry.Registry = nodes.dynamic_nodes_registry(),
    **kwargs,
) -> RuleExecutor:
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
