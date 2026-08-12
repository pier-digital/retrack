import pandas as pd
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

    assert isinstance(rm.dataframe_model, dict)

    payload = rm.model(example="test")

    assert isinstance(payload, pydantic.BaseModel)
    result = rm.validate(pd.DataFrame([{"example": "test"}]))
    assert isinstance(result, pd.DataFrame)


def test_validate_dict_with_model(valid_input_dict_before_validation):
    rm = RequestManager([Input(**valid_input_dict_before_validation)])

    assert issubclass(rm.model, pydantic.BaseModel)
    assert rm.model.model_validate({"example": 1111}) == rm.model(example="1111")


def test_validate_dict_with_none_value(valid_input_dict_before_validation):
    rm = RequestManager([Input(**valid_input_dict_before_validation)])

    assert issubclass(rm.model, pydantic.BaseModel)
    assert rm.model(example=None) == rm.model(example="Hello World")
    assert rm.model() == rm.model(example="Hello World")


def test_validate_dataframe_replaces_sentinel_strings_with_default(
    valid_input_dict_before_validation,
):
    """Sentinel strings count as null in the DataFrame path, matching StrFieldValidator."""
    rm = RequestManager([Input(**valid_input_dict_before_validation)])

    result = rm.validate(
        pd.DataFrame([{"example": v} for v in ["None", "", "null", None]])
    )

    assert result["example"].tolist() == ["Hello World"] * 4


def test_validate_dataframe_rejects_sentinel_strings_when_not_nullable(
    valid_input_dict_before_validation,
):
    """Without a default the input is not nullable, so sentinel strings must raise."""
    rm = RequestManager(
        [Input(**{**valid_input_dict_before_validation, "data": {"name": "example"}})]
    )

    for value in ["None", "", "null", None]:
        with pytest.raises(ValueError, match="not nullable"):
            rm.validate(pd.DataFrame([{"example": value}]))
