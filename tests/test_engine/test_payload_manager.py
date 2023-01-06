import pytest

from retack.engine.payload_manager import PayloadManager


def test_create_payload_manager_with_dict(valid_input_dict_before_validation):
    with pytest.raises(TypeError):
        PayloadManager(valid_input_dict_before_validation)


def test_create_payload_manager_with_list_of_dicts(valid_input_dict_before_validation):
    pm = PayloadManager([valid_input_dict_before_validation])
    assert len(pm.inputs) == 1
    assert pm.model is not None


def test_create_payload_manager_with_list_of_dicts_and_duplicate_names(
    valid_input_dict_before_validation,
):
    pm = PayloadManager(
        [valid_input_dict_before_validation, valid_input_dict_before_validation]
    )
    assert len(pm.inputs) == 1
    assert pm.model is not None


def test_create_payload_manager_with_invalid_input(valid_input_dict_before_validation):
    with pytest.raises(TypeError):
        PayloadManager([valid_input_dict_before_validation, "invalid"])


def test_validate_payload_with_valid_payload(valid_input_dict_before_validation):
    pm = PayloadManager([valid_input_dict_before_validation])
    payload = pm.model(example="test")
    assert pm.validate({"example": "test"})[0] == payload
