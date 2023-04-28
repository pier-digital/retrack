import typing

from retrack import nodes, validators
from retrack.nodes import BaseNode
from retrack.utils.registry import Registry


class Parser:
    def __init__(
        self,
        graph_data: dict,
        component_registry: Registry = nodes.registry(),
        validator_registry: Registry = validators.registry(),
    ):
        self.__components = {}
        self.__edges = None

        self._check_input_data(graph_data)

        self._set_components(graph_data, component_registry)
        self._set_edges()

        self._validate_graph(graph_data, validator_registry)

        self._set_indexes_by_name_map()
        self._set_indexes_by_kind_map()

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

    @staticmethod
    def _check_node_name(node_name: str, node_id: str):
        if node_name is None:
            raise ValueError(f"BaseNode {node_id} has no name")
        if not isinstance(node_name, str):
            raise TypeError(f"BaseNode {node_id} name must be a string")

    @property
    def components(self) -> typing.Dict[str, BaseNode]:
        return self.__components

    def _set_components(self, graph_data: dict, component_registry: Registry):
        for node_id, node_metadata in graph_data["nodes"].items():
            if node_id in self.__components:
                raise ValueError(f"Duplicate node id: {node_id}")

            node_name = node_metadata.get("name", None)
            self._check_node_name(node_name, node_id)

            node_name = node_name.lower()

            validation_model = component_registry.get(node_name)

            if validation_model is None:
                raise ValueError(f"Unknown node name: {node_name}")

            self.__components[node_id] = validation_model(**node_metadata)

    @property
    def edges(self) -> typing.List[typing.Tuple[str, str]]:
        return self.__edges

    def _set_edges(self):
        self.__edges = []

        for node_id, node in self.components.items():
            for _, output_connection in node.outputs:
                for c in output_connection.connections:
                    self.__edges.append((node_id, c.node))

    def _validate_graph(self, graph_data: dict, validator_registry: Registry):
        for validator_name, validator in validator_registry.data.items():
            if not validator.validate(graph_data=graph_data, edges=self.edges):
                raise ValueError(f"Invalid graph data: {validator_name}")

    def get_by_id(self, id_: str) -> BaseNode:
        return self.components.get(id_)

    @property
    def indexes_by_name_map(self) -> typing.Dict[str, typing.List[str]]:
        return self._indexes_by_name_map

    def _set_indexes_by_name_map(self):
        self._indexes_by_name_map = {}

        for node_id, node in self.components.items():
            node_name = node.__class__.__name__.lower()
            if node_name not in self._indexes_by_name_map:
                self._indexes_by_name_map[node_name] = []

            self._indexes_by_name_map[node_name].append(node_id)

    def get_by_name(self, name: str) -> typing.List[BaseNode]:
        return [self.get_by_id(id_) for id_ in self.indexes_by_name_map[name]]

    @property
    def indexes_by_kind_map(self) -> typing.Dict[str, typing.List[str]]:
        return self._indexes_by_kind_map

    def _set_indexes_by_kind_map(self):
        self._indexes_by_kind_map = {}

        for node_id, node in self.components.items():
            if node.kind() not in self._indexes_by_kind_map:
                self._indexes_by_kind_map[node.kind()] = []

            self._indexes_by_kind_map[node.kind()].append(node_id)

    def get_by_kind(self, kind: str) -> typing.List[BaseNode]:
        return [self.get_by_id(id_) for id_ in self.indexes_by_kind_map[kind]]
