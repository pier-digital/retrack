import typing

from retrack.engine.validators import registry as GLOBAL_VALIDATOR_REGISTRY
from retrack.nodes import BaseNode
from retrack.nodes import registry as GLOBAL_NODE_REGISTRY
from retrack.utils.registry import Registry


class Parser:
    def __init__(
        self,
        graph_data: dict,
        component_registry: Registry = GLOBAL_NODE_REGISTRY,
        validator_registry: Registry = GLOBAL_VALIDATOR_REGISTRY,
        unknown_node_error: bool = False,
    ):
        """Parses a dictionary of nodes and returns a dictionary of BaseNode objects.

        Args:
            data (dict): A dictionary of nodes.
            component_registry (Registry, optional): A registry of BaseNode objects. Defaults to GLOBAL_NODE_REGISTRY.
            validator_registry (Registry, optional): A registry of BaseValidator objects. Defaults to GLOBAL_VALIDATOR_REGISTRY.
            unknown_node_error (bool, optional): Whether to raise an error if an unknown node is found. Defaults to False.
        """
        Parser._check_input_data(graph_data)

        node_registry = Registry()
        self._indexes_by_kind_map = {}
        self._indexes_by_name_map = {}
        self.__edges = None

        for node_id, node_data in graph_data["nodes"].items():
            node_name = node_data.get("name", None)

            Parser._check_node_name(node_name, node_id)

            node_name = node_name.lower()

            validation_model = component_registry.get(node_name)
            if validation_model is not None:
                if node_name not in self._indexes_by_name_map:
                    self._indexes_by_name_map[node_name] = []

                self._indexes_by_name_map[node_name].append(node_id)

                node_data["id"] = node_id
                if node_id not in node_registry:
                    node = validation_model(**node_data)
                    node_registry.register(node_id, node)

                    if node.kind() not in self._indexes_by_kind_map:
                        self._indexes_by_kind_map[node.kind()] = []

                    self._indexes_by_kind_map[node.kind()].append(node_id)

            elif unknown_node_error:
                raise ValueError(f"Unknown node name: {node_name}")

        self._node_registry = node_registry

        for validator_name, validator in validator_registry.data.items():
            if not validator.validate(graph_data=graph_data, edges=self.edges):
                raise ValueError(f"Invalid graph data: {validator_name}")

    @staticmethod
    def _check_node_name(node_name: str, node_id: str):
        if node_name is None:
            raise ValueError(f"BaseNode {node_id} has no name")
        if not isinstance(node_name, str):
            raise TypeError(f"BaseNode {node_id} name must be a string")

    @staticmethod
    def _check_input_data(data: dict):
        if not isinstance(data, dict):
            raise TypeError(
                "Data must be a dictionary. Instead got: " + str(type(data))
            )
        if "nodes" not in data:
            raise ValueError("No nodes found in data")
        if not isinstance(data["nodes"], dict):
            raise TypeError(
                "BaseNodes must be a dictionary. Instead got: "
                + str(type(data["nodes"]))
            )

    @property
    def nodes(self) -> typing.Dict[str, BaseNode]:
        return self._node_registry.data

    @property
    def edges(self) -> typing.List[typing.Tuple[str, str]]:
        if self.__edges is None:
            edges = []

            for node_id, node in self.nodes.items():
                for _, output_connection in node.outputs:
                    for c in output_connection.connections:
                        edges.append((node_id, c.node))

            self.__edges = edges

        return self.__edges

    @property
    def data(self) -> dict:
        return {i: j.dict(by_alias=True) for i, j in self.nodes.items()}

    @property
    def tokens(self) -> dict:
        """Returns a dictionary of tokens (node name) and their associated node ids."""
        return self._indexes_by_name_map

    @property
    def indexes_by_kind_map(self) -> dict:
        """Returns a dictionary of node kinds and their associated node ids."""
        return self._indexes_by_kind_map

    def get_node_by_id(self, node_id: str) -> BaseNode:
        return self._node_registry.get(node_id)

    def get_nodes_by_name(self, node_name: str) -> typing.List[BaseNode]:
        node_name = node_name.lower()
        return [self.get_node_by_id(i) for i in self.tokens.get(node_name, [])]

    def get_nodes_by_multiple_names(self, node_names: list) -> typing.List[BaseNode]:
        all_nodes = []
        for node_name in node_names:
            nodes = self.get_nodes_by_name(node_name)
            if nodes is not None:
                all_nodes.extend(nodes)

        return all_nodes

    def get_nodes_by_kind(self, kind: str) -> typing.List[BaseNode]:
        return [self.get_node_by_id(i) for i in self.indexes_by_kind_map.get(kind, [])]
