import typing

import hashlib

from retrack import nodes, validators
from retrack.utils.registry import Registry
from retrack.utils.component_registry import ComponentRegistry
from retrack.nodes.base import NodeKind
import json

from unidecode import unidecode


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
        self.__graph_data = graph_data
        self.__components_registry = ComponentRegistry()
        self._execution_order = None
        self.__edges = None
        self._raise_if_null_version = raise_if_null_version
        self._validate_version = validate_version

        self._check_input_data(self.graph_data)

        self._set_components(nodes_registry, dynamic_nodes_registry)
        self._set_edges()

        self._validate_graph(validator_registry)

        self._set_execution_order()
        self._set_version()
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
    def components(self) -> typing.Dict[str, nodes.BaseNode]:
        return self.components_registry.data

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
                "Nodes must be a dictionary. Instead got: " + str(type(data["nodes"]))
            )

    @staticmethod
    def _check_node_name(node_name: str, node_id: str):
        if node_name is None:
            raise ValueError(f"Node {node_id} has no name")
        if not isinstance(node_name, str):
            raise TypeError(f"Node {node_id} name must be a string")

    def _set_components(
        self, nodes_registry: Registry, dynamic_nodes_registry: Registry
    ):
        for node_id, node_metadata in self.graph_data["nodes"].items():
            if node_id in self.components_registry:
                raise ValueError(f"Duplicate node id: {node_id}")

            node_name = node_metadata.get("name", None)
            self._check_node_name(node_name, node_id)

            node_name = node_name.lower()

            node_factory = dynamic_nodes_registry.get(node_name)

            if node_factory is not None:
                validation_model = node_factory(**node_metadata)
            else:
                validation_model = nodes_registry.get(node_name)

            if validation_model is None:
                raise ValueError(f"Unknown node name: {node_name}")

            self.components_registry.register(
                node_id, validation_model(**node_metadata)
            )

    @property
    def edges(self) -> typing.List[typing.Tuple[str, str]]:
        return self.__edges

    def _set_edges(self):
        self.__edges = []

        for node_id, node in self.components.items():
            for _, output_connection in node.outputs:
                for c in output_connection.connections:
                    self.__edges.append((node_id, c.node))

    def _validate_graph(self, validator_registry: Registry):
        for validator_name, validator in validator_registry.data.items():
            if not validator.validate(graph_data=self.graph_data, edges=self.edges):
                raise ValueError(f"Invalid graph data: {validator_name}")

    def get_by_id(self, id_: str) -> nodes.BaseNode:
        return self.components.get(id_)

    @property
    def execution_order(self) -> typing.List[str]:
        return self._execution_order

    def _set_execution_order(self):
        start_nodes = self.components_registry.get_by_name("start")

        self._execution_order = self._walk(start_nodes[0].id, [])

    def _walk(self, actual_id: str, skiped_ids: list):
        skiped_ids.append(actual_id)

        output_ids = self.components_registry.get_node_output_connections(actual_id)

        for next_id in output_ids:
            if next_id not in skiped_ids:
                next_node_input_ids = (
                    self.components_registry.get_node_input_connections(next_id)
                )
                run_next = True
                for next_node_input_id in next_node_input_ids:
                    if next_node_input_id not in skiped_ids:
                        run_next = False
                        break

                if run_next:
                    self._walk(next_id, skiped_ids)

        return skiped_ids

    def _set_version(self):
        self._version = self.graph_data.get("version", None)

        graph_json_content = (
            json.dumps(self.graph_data["nodes"], ensure_ascii=False)
            .replace(": ", ":")
            .replace("\\", "")
            .replace('"', "")
            .replace(", ", ",")
        )
        graph_json_content = unidecode(graph_json_content, errors="strict")
        calculated_hash = hashlib.sha256(graph_json_content.encode()).hexdigest()[:10]

        if self.version is None:
            if self._raise_if_null_version:
                raise ValueError("Missing version")

            self._version = f"{calculated_hash}.dynamic"
        else:
            file_version_hash = self.version.split(".")[0]

            if file_version_hash != calculated_hash and self._validate_version:
                raise ValueError(
                    f"Invalid version. Graph data has changed and the hash is different: {calculated_hash} != {file_version_hash}"
                )

    def _set_input_nodes_from_connectors(self):
        connector_nodes = self.components_registry.get_by_kind(NodeKind.CONNECTOR)

        for connector_node in connector_nodes:
            input_nodes = connector_node.generate_input_nodes()
            for input_node in input_nodes:
                self.components_registry.register(input_node.id, input_node)
