import json

from unidecode import unidecode
import hashlib
from retrack.utils.registry import Registry
from retrack.utils.component_registry import ComponentRegistry


def validate_version(
    graph_data: dict, raise_if_null_version: bool, validate_version: bool
) -> str:
    version = graph_data.get("version", None)

    graph_json_content = (
        json.dumps(graph_data["nodes"], ensure_ascii=False)
        .replace(": ", ":")
        .replace("\\", "")
        .replace('"', "")
        .replace(", ", ",")
    )
    graph_json_content = unidecode(graph_json_content, errors="strict")
    calculated_hash = hashlib.sha256(graph_json_content.encode()).hexdigest()[:10]

    if version is None:
        if raise_if_null_version:
            raise ValueError("Missing version")

        return f"{calculated_hash}.dynamic"

    file_version_hash = version.split(".")[0]

    if file_version_hash != calculated_hash and validate_version:
        raise ValueError(
            f"Invalid version. Graph data has changed and the hash is different: {calculated_hash} != {file_version_hash}"
        )

    return version


def validate_data(data: dict) -> dict:
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary. Instead got: " + str(type(data)))
    if "nodes" not in data:
        raise ValueError("No nodes found in data")
    if not isinstance(data["nodes"], dict):
        raise TypeError(
            "Nodes must be a dictionary. Instead got: " + str(type(data["nodes"]))
        )
    return data


def validate_with_validators(
    graph_data: dict, edges: dict, validator_registry: Registry
):
    for validator_name, validator in validator_registry.data.items():
        if not validator.validate(graph_data=graph_data, edges=edges):
            raise ValueError(f"Invalid graph data: {validator_name}")


def check_node_name(node_name: str, node_id: str):
    if node_name is None:
        raise ValueError(f"Node {node_id} has no name")
    if not isinstance(node_name, str):
        raise TypeError(f"Node {node_id} name must be a string")


def create_component_registry(
    graph_data: dict, nodes_registry: Registry, dynamic_nodes_registry: Registry
) -> ComponentRegistry:
    components_registry = ComponentRegistry()
    graph_data = validate_data(graph_data)
    for node_id, node_metadata in graph_data["nodes"].items():
        if node_id in components_registry:
            raise ValueError(f"Duplicate node id: {node_id}")

        node_name = node_metadata.get("name", None)
        check_node_name(node_name, node_id)

        node_name = node_name.lower()

        node_factory = dynamic_nodes_registry.get(node_name)

        if node_factory is not None:
            validation_model = node_factory(**node_metadata)
        else:
            validation_model = nodes_registry.get(node_name)

        if validation_model is None:
            raise ValueError(f"Unknown node name: {node_name}")

        components_registry.register(node_id, validation_model(**node_metadata))

    return components_registry


def walk(actual_id: str, skiped_ids: list, components_registry: ComponentRegistry):
    skiped_ids.append(actual_id)

    output_ids = components_registry.get_node_output_connections(actual_id)

    for next_id in output_ids:
        if next_id not in skiped_ids:
            next_node_input_ids = components_registry.get_node_input_connections(
                next_id
            )
            run_next = True
            for next_node_input_id in next_node_input_ids:
                if next_node_input_id not in skiped_ids:
                    run_next = False
                    break

            if run_next:
                walk(next_id, skiped_ids, components_registry)

    return skiped_ids


def get_execution_order(components_registry: ComponentRegistry):
    start_nodes = components_registry.get_by_name("start")

    return walk(start_nodes[0].id, [], components_registry)
