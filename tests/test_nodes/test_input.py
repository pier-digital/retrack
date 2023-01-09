from retack.nodes.inputs import Input


def test_input_model(
    valid_input_dict_before_validation, valid_input_dict_after_validation
):
    input_model = Input(**valid_input_dict_before_validation)

    assert input_model.dict(by_alias=True) == valid_input_dict_after_validation
