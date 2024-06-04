from retrack.nodes.inputs import Input


def test_input_node(
    valid_input_dict_before_validation, valid_input_dict_after_validation
):
    input_node = Input(**valid_input_dict_before_validation)

    assert input_node.model_dump(by_alias=True) == valid_input_dict_after_validation


def test_input_with_empty_string_as_default(valid_input_dict_before_validation):
    valid_input_dict_before_validation["data"]["default"] = ""
    input_node = Input(**valid_input_dict_before_validation)

    assert input_node.data.default is None
