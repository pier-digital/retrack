import pytest

from retrack.engine.request_manager import RequestManager
from retrack.nodes.inputs import Input
import pandas as pd

def test_create_request_manager(valid_input_dict_before_validation):
    with pytest.raises(TypeError):
        RequestManager(Input(**valid_input_dict_before_validation))


def test_create_request_manager_with_list_of_inputs(valid_input_dict_before_validation):
    pm = RequestManager([Input(**valid_input_dict_before_validation)])
    assert len(pm.inputs) == 1
    assert pm.model is not None


def test_create_request_manager_with_list_of_inputs_and_duplicate_names(
    valid_input_dict_before_validation,
):
    pm = RequestManager(
        [
            Input(**valid_input_dict_before_validation),
            Input(**valid_input_dict_before_validation),
        ]
    )
    assert len(pm.inputs) == 1
    assert pm.model is not None


def test_create_request_manager_with_invalid_input(valid_input_dict_before_validation):
    with pytest.raises(TypeError):
        RequestManager([Input(**valid_input_dict_before_validation), "invalid"])


def test_validate_payload_with_valid_payload(valid_input_dict_before_validation):
    pm = RequestManager([Input(**valid_input_dict_before_validation)])
    payload = pm.model(example="test")
    assert pm.validate(pd.DataFrame([{{"example": "test"}}]))[0] == payload
