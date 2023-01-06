from retack.models.inputs import InputModel


def test_input_model(
    valid_input_dict_before_validation, valid_input_dict_after_validation
):
    input_model = InputModel(**valid_input_dict_before_validation)

    assert input_model.dict(by_alias=True) == valid_input_dict_after_validation
