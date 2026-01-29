import typing

import pandas as pd
from retrack.nodes.base import BaseNode
from retrack.utils.constants import EXCLUDED_NODE_TYPES, FILTER_SUFFIX, NULL_SUFFIX


def is_excluded_node(node_type: str) -> bool:
    return node_type in EXCLUDED_NODE_TYPES


def is_filtered_connection(name: typing.Any) -> bool:
    """Check if connection name contains filter or null suffix."""
    if name is None:
        return False
    lowered = str(name).lower()
    return FILTER_SUFFIX in lowered or NULL_SUFFIX in lowered


def to_list(input_list):
    if isinstance(input_list, pd.Series):
        input_list = input_list.to_list()

    return input_list


def to_metadata(node: BaseNode) -> typing.List[dict]:
    """Serialize node.data into a list of {name, value}, ignoring alias/default."""
    data = getattr(node, "data", None)
    if data is None:
        return []

    try:
        data_dict = data.model_dump()
    except Exception:
        data_dict = getattr(data, "__dict__", {})

    filtered = {
        key: value
        for key, value in data_dict.items()
        if key not in {"alias", "default"}
    }

    return [{"name": key, "value": value} for key, value in filtered.items()]


def serialize_connections(
    inputs_or_outputs: typing.Any,
    node_id: str,
    connection_type: str,
    execution: "typing.Any",
) -> list:
    """Transform connection models into serialized list with values and source name.

    Args:
        inputs_or_outputs: Pydantic model or None with connection data
        node_id: Current node ID
        connection_type: 'input' or 'output'
        execution: Execution instance for fetching state data

    Returns:
        List of {node_id, name, values, source}

    Note: Values are stored as node_id@output_name in states.
    For inputs: key is remote_node_id@remote_output_name
    For outputs: key is current_node_id@current_output_name
    """
    if inputs_or_outputs is None or not hasattr(inputs_or_outputs, "model_dump"):
        return []

    connection_target_key = "output" if connection_type == "input" else "input"

    serialized_connections = []
    for (
        input_or_output_name,
        input_or_output,
    ) in inputs_or_outputs.model_dump().items():
        connections = input_or_output.get("connections", [])

        for connection in connections:
            remote_node_id = connection.get("node")
            remote_name = connection.get(connection_target_key)

            try:
                if connection_type == "input":
                    state_key = f"{remote_node_id}@{remote_name}"
                else:
                    state_key = f"{node_id}@{input_or_output_name}"

                values = execution.get_state_data(
                    state_key,
                    constants=execution.constants,
                    filter_by=None,
                ).tolist()

                values = [None if pd.isna(value) else value for value in values]
            except Exception:
                values = []

            target_name = (
                remote_name if connection_type == "output" else input_or_output_name
            )
            source_name = (
                input_or_output_name if connection_type == "output" else remote_name
            )

            serialized_connections.append(
                {
                    "node_id": remote_node_id,
                    "target_name": target_name,
                    "values": values,
                    "source_name": source_name,
                }
            )

    return serialized_connections


def explode_nodes_by_values(nodes: typing.List[dict]) -> typing.List[typing.List[dict]]:
    """Explode nodes by values array into array of arrays per value index.

    For each node, finds all input/output values arrays and determines max length.
    Returns a list of lists where each sublist contains all nodes for that value index,
    with 'values' array replaced by 'value' (singular) containing the specific value
    or null if missing/empty.

    Args:
        nodes: List of normalized node dictionaries

    Returns:
        List of lists: [[node1_idx0, node2_idx0, ...], [node1_idx1, node2_idx1, ...], ...]
    """
    if not nodes:
        return []

    max_length = 0
    for node in nodes:
        for connection_list in [node.get("inputs", []), node.get("outputs", [])]:
            for connection in connection_list:
                max_length = max(max_length, len(connection.get("values", [])))

    if max_length == 0:
        max_length = 1

    exploded_nodes_by_index = []

    for idx in range(max_length):
        nodes_for_index = []

        for node in nodes:
            exploded_node = {
                "id": node["id"],
                "name": node["name"],
                "type": node["type"],
                "inputs": [],
                "outputs": [],
                "default": node.get("default"),
                "data": node.get("data", []),
            }

            for input_conn in node.get("inputs", []):
                values = input_conn.get("values", [])
                value = values[idx] if idx < len(values) else None

                exploded_node["inputs"].append(
                    {
                        "node_id": input_conn.get("node_id"),
                        "target_name": input_conn.get("target_name"),
                        "value": value,
                        "source_name": input_conn.get("source_name"),
                    }
                )

            for output_conn in node.get("outputs", []):
                values = output_conn.get("values", [])
                value = values[idx] if idx < len(values) else None

                exploded_node["outputs"].append(
                    {
                        "node_id": output_conn.get("node_id"),
                        "target_name": output_conn.get("target_name"),
                        "value": value,
                        "source_name": output_conn.get("source_name"),
                    }
                )

            nodes_for_index.append(exploded_node)

        exploded_nodes_by_index.append(nodes_for_index)

    return exploded_nodes_by_index


def normalize_execution_for_debug(
    exploded_nodes: typing.List[typing.List[dict]],
    apply_filters: bool = True,
) -> typing.List[dict]:
    """Transform exploded nodes into debug format with inputs, results, nodes, and connections.

    Args:
        exploded_nodes: List of lists from explode_nodes_by_values
        apply_filters: Whether to apply exclusion filters (node types, void connections, null values)

    Returns:
        List of normalized records, one per value index
    """
    normalized_records = []

    for nodes_at_index in exploded_nodes:
        inputs = []
        seen_input_names = set()
        for node in nodes_at_index:
            if node.get("type") == "Input":
                node_name = node.get("name")
                if node_name not in seen_input_names:
                    outputs = node.get("outputs", [])
                    if outputs:
                        inputs.append(
                            {
                                "name": node_name,
                                "value": outputs[0].get("value"),
                            }
                        )
                    seen_input_names.add(node_name)

        outputs = []
        for node in nodes_at_index:
            if node.get("type") == "Output":
                inputs_list = node.get("inputs", [])
                node_name = node.get("name")
                if inputs_list:
                    first_input = inputs_list[0]
                    value = first_input.get("value")

                    message = None
                    for item in node.get("data", []):
                        if item.get("name") == "message":
                            message = item.get("value")
                            break

                    if value is not None and not (
                        isinstance(value, float) and pd.isna(value)
                    ):
                        outputs.append(
                            {
                                "name": "output",
                                "value": value,
                                "message": message,
                            }
                        )

        nodes_info = [
            {
                "id": node.get("id"),
                "name": node.get("name"),
                "type": node.get("type"),
                "default": node.get("default"),
            }
            for node in nodes_at_index
            if not apply_filters or not is_excluded_node(node.get("type"))
        ]

        connections = []
        seen_connections = set()

        for node in nodes_at_index:
            node_type = node.get("type")
            if apply_filters and is_excluded_node(node_type):
                continue

            node_id = node.get("id")
            node_name = node.get("name")

            for input_conn in node.get("inputs", []):
                value = input_conn.get("value")
                conn_name = input_conn.get("target_name")
                if apply_filters and is_filtered_connection(conn_name):
                    continue

                connection_key = (node_id, conn_name, "input")
                if connection_key not in seen_connections:
                    seen_connections.add(connection_key)
                    connections.append(
                        {
                            "node_id": node_id,
                            "node_type": node_type,
                            "node_name": node_name,
                            "connection_type": "input",
                            "connection_name": conn_name,
                            "value": value,
                        }
                    )

            for output_conn in node.get("outputs", []):
                value = output_conn.get("value")
                conn_name = output_conn.get("source_name")
                if apply_filters and is_filtered_connection(conn_name):
                    continue

                connection_key = (node_id, conn_name, "output")
                if connection_key not in seen_connections:
                    seen_connections.add(connection_key)
                    connections.append(
                        {
                            "node_id": node_id,
                            "node_type": node_type,
                            "node_name": node_name,
                            "connection_type": "output",
                            "connection_name": conn_name,
                            "value": value,
                        }
                    )

        normalized_records.append(
            {
                "inputs": inputs,
                "outputs": outputs,
                "nodes": nodes_info,
                "connections": connections,
            }
        )

    return normalized_records
