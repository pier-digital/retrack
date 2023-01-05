from retack.models.inputs import InputModel


def test_input_model():
    input_data = {
        "id": 1,
        "data": {"name": "Example", "default": "Hello World"},
        "inputs": {},
        "outputs": {
            "output_value": {
                "connections": [{"node": 0, "input": "input_void", "data": {}}]
            }
        },
        "position": [-444.37109375, 175.50390625],
        "name": "Input",
    }

    input_model = InputModel(**input_data)

    assert input_model.dict(by_alias=True) == {
        "id": "1",
        "data": {"name": "Example", "default": "Hello World"},
        "inputs": {"input_void": None},
        "outputs": {
            "output_value": {"connections": [{"node": "0", "input": "input_void"}]}
        },
    }
