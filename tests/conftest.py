import pytest


@pytest.fixture
def valid_input_dict_before_validation() -> dict:
    return {
        "id": 1,
        "data": {"name": "example", "default": "Hello World"},
        "inputs": {},
        "outputs": {
            "output_value": {
                "connections": [{"node": 0, "input": "input_void", "data": {}}]
            }
        },
        "position": [-444.37109375, 175.50390625],
        "name": "Input",
    }


@pytest.fixture
def valid_input_dict_after_validation() -> dict:
    return {
        "id": "1",
        "data": {"name": "example", "default": "Hello World"},
        "inputs": {"input_void": None},
        "outputs": {
            "output_value": {"connections": [{"node": "0", "input": "input_void"}]}
        },
    }
