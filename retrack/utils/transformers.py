import typing

import pandas as pd
from retrack.nodes.base import BaseNode


def to_list(input_list):
    if isinstance(input_list, pd.Series):
        input_list = input_list.to_list()

    return input_list


def to_normalized_dict(df: pd.DataFrame, key_name: str = "name") -> typing.List[dict]:
    """Convert DataFrame columns to list of dicts with name and values."""
    return [
        {key_name: k, "values": list(v.values())}
        for k, v in df.to_dict(orient="dict").items()
    ]


def to_metadata(node: BaseNode) -> list:
    """Serialize arbitrary node data into a flat list of key/value pairs."""
    data = getattr(node, "data", None)
    if data is None:
        return []

    if hasattr(data, "model_dump"):
        payload = data.model_dump()
    elif hasattr(data, "dict"):
        payload = data.dict()
    elif isinstance(data, dict):
        payload = data
    else:
        payload = getattr(data, "__dict__", {})

    return [{"key": k, "value": v} for k, v in payload.items()]


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
                current_node_filter = execution.filters.get(node_id, None)

                if connection_type == "input":
                    state_key = f"{remote_node_id}@{remote_name}"
                else:
                    state_key = f"{node_id}@{input_or_output_name}"

                values = execution.get_state_data(
                    state_key,
                    constants=execution.constants,
                    filter_by=current_node_filter,
                ).tolist()
            except Exception:
                values = []

            name = remote_name if connection_type == "input" else input_or_output_name
            source = input_or_output_name if connection_type == "input" else remote_name

            serialized_connections.append(
                {
                    "node_id": remote_node_id,
                    "name": name,
                    "values": values,
                    "source": source,
                }
            )

    return serialized_connections


def process_node_connections(
    connections_dict: dict,
    get_state_data_func: typing.Callable,
    constants: dict,
    filter_by: typing.Any,
    name_field: str,
    target_field: str,
    target_key: str,
    node_id: str = None,
    use_node_id_for_values: bool = False,
) -> typing.List[dict]:
    """Process node connections and extract values from state data.

    Args:
        connections_dict: Dictionary with connection information (name -> connections).
        get_state_data_func: Function to retrieve state data.
        constants: Constants dictionary to pass to get_state_data_func.
        filter_by: Filter to apply when getting state data.
        name_field: Name of the field for the connection name (e.g., 'input_name' or 'output_name').
        target_field: Name of the target field (e.g., 'output_name' or 'input_name').
        target_key: Key to use from connection dict (e.g., 'output' or 'input').
        node_id: ID of the current node (required when use_node_id_for_values=True).
        use_node_id_for_values: If True, fetch values from current node instead of connection node.

    Returns:
        List of dictionaries with connection information and values.
    """

    def key(connection, connection_name):
        """Build state key from connection node and field."""
        if use_node_id_for_values:
            return f"{node_id}@{connection_name}"
        return f"{connection['node']}@{connection[target_key]}"

    def values(connections, connection_name):
        """Fetch and flatten values from all connections."""

        def fetch(connection):
            try:
                return get_state_data_func(
                    key(connection, connection_name),
                    constants=constants,
                    filter_by=filter_by,
                ).tolist()
            except Exception:
                return []

        return [value for connection in connections for value in fetch(connection)]

    def serialize(name, connection, values):
        """Create standardized connection info dictionary."""
        return {
            name_field: name,
            target_field: connection[target_key],
            "id": connection["node"],
            "values": values,
        }

    return [
        serialize(name, connections_list[-1], values(connections_list, name))
        for name, connections in connections_dict.items()
        if (connections_list := connections.get("connections", []))
    ]
