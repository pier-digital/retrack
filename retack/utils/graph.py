def get_element_connections(element, is_input: bool = True):
    element_dict = element.dict(by_alias=True)
    connectors = element_dict.get("inputs" if is_input else "outputs", {})
    result = []

    for _, value in connectors.items():
        for connection in value["connections"]:
            result.append(connection["node"])
    return result


def walk(parser, actual_id: str, skiped_ids=[], callback=None):
    element = parser.get_element_by_id(actual_id)
    if callback:
        callback(element.id)
    skiped_ids.append(actual_id)

    output_ids = get_element_connections(element, is_input=False)

    for next_id in output_ids:
        if next_id not in skiped_ids:
            next_element = parser.get_element_by_id(next_id)
            next_element_input_ids = get_element_connections(
                next_element, is_input=True
            )
            run_next = True
            for next_element_input_id in next_element_input_ids:
                if next_element_input_id not in skiped_ids:
                    run_next = False
                    break

            if run_next:
                walk(parser, next_id, skiped_ids, callback)

    return skiped_ids


def get_execution_order(parser):
    start_elements = parser.get_elements_by_name("start")
    if len(start_elements) == 0:
        raise ValueError("No start element found")

    return walk(parser, start_elements[0].id)
