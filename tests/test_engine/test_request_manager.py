import pandas as pd
import pandera
import pydantic
import pytest

from retrack.engine.request_manager import RequestManager
from retrack.nodes.inputs import Input


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
    rm = RequestManager([Input(**valid_input_dict_before_validation)])

    assert issubclass(rm.model, pydantic.BaseModel)

    assert isinstance(rm.dataframe_model, pandera.api.pandas.container.DataFrameSchema)

    payload = rm.model(example="test")

    assert isinstance(payload, pydantic.BaseModel)
    result = rm.validate(pd.DataFrame([{"example": "test"}]))
    assert isinstance(result, pd.DataFrame)
