import typing

from retrack.nodes import BaseNode
from retrack.nodes import registry as GLOBAL_NODE_REGISTRY
from retrack.utils.registry import Registry

INPUT_TOKENS = ["input"]

OUTPUT_TOKENS = ["booloutput"]

CONSTANT_TOKENS = ["constant", "list", "bool"]


class Parser:
    def __init__(
        self,
        data: dict,
        component_registry: Registry = GLOBAL_NODE_REGISTRY,
        unknown_node_error: bool = False,
    ):
        Parser._check_input_data(data)

        node_registry = Registry()
        tokens = {}

        for node_id, node_data in data["nodes"].items():
            node_name = node_data.get("name", None)

            Parser._check_node_name(node_name, node_id)

            node_name = node_name.lower()

            validation_model = component_registry.get(node_name)
            if validation_model is not None:
                if node_name not in tokens:
                    tokens[node_name] = []

                tokens[node_name].append(node_id)

                node_data["id"] = node_id
                if node_id not in node_registry:
                    node_registry.register(node_id, validation_model(**node_data))
            elif unknown_node_error:
                raise ValueError(f"Unknown node name: {node_name}")

        self._node_registry = node_registry
        self._tokens = tokens

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
    def data(self) -> dict:
        return {i: j.dict(by_alias=True) for i, j in self.nodes.items()}

    @property
    def tokens(self) -> dict:
        return self._tokens

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
        if kind == "input":
            return self.get_nodes_by_multiple_names(INPUT_TOKENS)
        if kind == "output":
            return self.get_nodes_by_multiple_names(OUTPUT_TOKENS)
        if kind == "constant":
            return self.get_nodes_by_multiple_names(CONSTANT_TOKENS)

        return []
