from retrack.nodes.inputs import Input


def test_input_node(
    valid_input_dict_before_validation, valid_input_dict_after_validation
):
    input_node = Input(**valid_input_dict_before_validation)

    assert input_node.dict(by_alias=True) == valid_input_dict_after_validation
