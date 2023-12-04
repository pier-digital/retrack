import typing


from retrack import nodes, validators
from retrack.utils.registry import Registry
from retrack.utils.component_registry import ComponentRegistry
from retrack.nodes.base import NodeKind
from retrack.utils import graph


class Parser:
    def __init__(
        self,
        graph_data: dict,
        nodes_registry: Registry = nodes.registry(),
        dynamic_nodes_registry: Registry = nodes.dynamic_nodes_registry(),
        validator_registry: Registry = validators.registry(),
        raise_if_null_version: bool = False,
        validate_version: bool = True,
    ):
        self.__components_registry = graph.create_component_registry(
            graph_data, nodes_registry, dynamic_nodes_registry
        )
        self._version = graph.validate_version(
            graph_data, raise_if_null_version, validate_version
        )
        self.__graph_data = graph_data

        graph.validate_with_validators(
            self.graph_data,
            self.components_registry.calculate_edges(),
            validator_registry,
        )

        self._execution_order = graph.get_execution_order(self.components_registry)

        self._set_input_nodes_from_connectors()

    @property
    def graph_data(self) -> dict:
        return self.__graph_data

    @property
    def version(self) -> str:
        return self._version

    @property
    def components_registry(self) -> ComponentRegistry:
        return self.__components_registry

    @property
    def execution_order(self) -> typing.List[str]:
        return self._execution_order

    def _set_input_nodes_from_connectors(self):
        connector_nodes = self.components_registry.get_by_kind(NodeKind.CONNECTOR)

        for connector_node in connector_nodes:
            input_nodes = connector_node.generate_input_nodes()
            for input_node in input_nodes:
                self.components_registry.register(input_node.id, input_node)
