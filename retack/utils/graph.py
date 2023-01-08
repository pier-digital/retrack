def get_node_connections(node, is_input: bool = True, filter_by_connector=None):
    if isinstance(node, dict):
        node_dict = node
    else:
        node_dict = node.dict(by_alias=True)
    connectors = node_dict.get("inputs" if is_input else "outputs", {})
    result = []

    for connector_name, value in connectors.items():
        if filter_by_connector is not None and connector_name != filter_by_connector:
            continue

        for connection in value["connections"]:
            result.append(connection["node"])
    return result


def walk(parser, actual_id: str, skiped_ids=[], callback=None):
    node = parser.get_node_by_id(actual_id)
    if callback:
        callback(node.id)
    skiped_ids.append(actual_id)

    output_ids = get_node_connections(node, is_input=False)

    for next_id in output_ids:
        if next_id not in skiped_ids:
            next_node = parser.get_node_by_id(next_id)

            next_node_input_ids = get_node_connections(next_node, is_input=True)
            run_next = True
            for next_node_input_id in next_node_input_ids:
                if next_node_input_id not in skiped_ids:
                    run_next = False
                    break

            if run_next:
                walk(parser, next_id, skiped_ids, callback)

    return skiped_ids


def get_execution_order(parser):
    start_nodes = parser.get_nodes_by_name("start")
    if len(start_nodes) == 0:
        raise ValueError("No start node found")
    elif len(start_nodes) > 1:
        raise ValueError("Multiple start nodes found")

    return walk(parser, start_nodes[0].id)
