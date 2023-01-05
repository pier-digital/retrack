from retack.models import ModelRegistry
from retack.models import model_registry as GLOBAL_MODEL_REGISTRY


class Parser:
    def __init__(
        self,
        data: dict,
        model_registry: ModelRegistry = GLOBAL_MODEL_REGISTRY,
    ):
        Parser._check_input_data(data)

        output_data = {}

        for node_id, node_data in data["nodes"].items():
            node_name = node_data.get("name", None)

            Parser._check_node_name(node_name, node_id)

            validation_model = model_registry.get(node_name)
            if validation_model is not None:
                node_data["id"] = node_id
                output_data[node_id] = validation_model(**node_data).dict(by_alias=True)

        self._data = output_data

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
    def data(self) -> dict:
        return self._data
