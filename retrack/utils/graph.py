import hashlib
import json

from unidecode import unidecode

from retrack.utils.component_registry import ComponentRegistry
from retrack.utils.registry import Registry
from retrack.utils import exceptions


def validate_version(
    graph_data: dict, raise_if_null_version: bool, validate_version: bool
) -> str:
    version = graph_data.get("version", None)

    graph_json_content = (
        json.dumps(graph_data["nodes"], ensure_ascii=False, separators=(",", ":"))
        .replace("\\", "")
        .replace('"', "")
    )
    graph_json_content = unidecode(graph_json_content, errors="strict")
    calculated_hash = hashlib.sha256(graph_json_content.encode()).hexdigest()[:10]

    if version is None:
        if raise_if_null_version:
            raise exceptions.InvalidVersionException(
                "Missing version. "
                + "Make sure to set a version in the graph data or set raise_if_null_version to False."
            )

        return f"{calculated_hash}.dynamic"

    file_version_hash = version.split(".")[0]

    if file_version_hash != calculated_hash and validate_version:
        raise exceptions.InvalidVersionException(
            "Invalid version. "
            + f"Graph data has changed and the hash is different: {calculated_hash} != {file_version_hash}"
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
