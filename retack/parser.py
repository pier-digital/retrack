import typing

import pydantic

from retack.nodes import Registry
from retack.nodes import model_registry as GLOBAL_MODEL_REGISTRY

INPUT_TOKENS = ["input"]

OUTPUT_TOKENS = ["booloutput"]

CONSTANT_TOKENS = ["constant", "list", "bool"]


class Parser:
    def __init__(
        self,
        data: dict,
        model_registry: Registry = GLOBAL_MODEL_REGISTRY,
        unknown_node_error: bool = False,
    ):
        Parser._check_input_data(data)

        element_registry = Registry()
        tokens = {}

        for node_id, node_data in data["nodes"].items():
            node_name = node_data.get("name", None)

            Parser._check_node_name(node_name, node_id)

            node_name = node_name.lower()

            validation_model = model_registry.get(node_name)
            if validation_model is not None:
                if node_name not in tokens:
                    tokens[node_name] = []

                tokens[node_name].append(node_id)

                node_data["id"] = node_id
                if node_id not in element_registry:
                    element_registry.register(node_id, validation_model(**node_data))
            elif unknown_node_error:
                raise ValueError(f"Unknown node name: {node_name}")

        self._element_registry = element_registry
        self._tokens = tokens

    @staticmethod
    def _check_node_name(node_name: str, node_id: str):
        if node_name is None:
            raise ValueError(f"Node {node_id} has no name")
        if not isinstance(node_name, str):
            raise TypeError(f"Node {node_id} name must be a string")

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

    @property
    def elements(self) -> typing.Dict[str, pydantic.BaseModel]:
        return self._element_registry.data

    @property
    def data(self) -> dict:
        return {i: j.dict(by_alias=True) for i, j in self.elements.items()}

    @property
    def tokens(self) -> dict:
        return self._tokens

    def get_element_by_id(self, element_id: str) -> pydantic.BaseModel:
        return self._element_registry.get(element_id)

    def get_elements_by_name(
        self, element_name: str
    ) -> typing.List[pydantic.BaseModel]:
        element_name = element_name.lower()
        return [self.get_element_by_id(i) for i in self.tokens.get(element_name, [])]

    def get_elements_by_multiple_names(
        self, element_names: list
    ) -> typing.List[pydantic.BaseModel]:
        all_elements = []
        for node_name in element_names:
            elements = self.get_elements_by_name(node_name)
            if elements is not None:
                all_elements.extend(elements)

        return all_elements

    def get_elements_by_kind(self, kind: str) -> typing.List[pydantic.BaseModel]:
        if kind == "input":
            return self.get_elements_by_multiple_names(INPUT_TOKENS)
        if kind == "output":
            return self.get_elements_by_multiple_names(OUTPUT_TOKENS)
        if kind == "constant":
            return self.get_elements_by_multiple_names(CONSTANT_TOKENS)

        return []

    def get_name_by_id(self, element_id: str) -> str:
        for name, ids in self.tokens.items():
            if element_id in ids:
                return name

        raise ValueError(f"Element {element_id} not found")
