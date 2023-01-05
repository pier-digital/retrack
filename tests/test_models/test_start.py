from retack.models.start import StartModel


def test_start_model():
    input_data = {
        "id": 0,
        "data": {},
        "inputs": {},
        "outputs": {
            "output_void": {
                "connections": [
                    {"node": 3, "input": "input_void", "data": {}},
                    {"node": 4, "input": "input_void", "data": {}},
                ]
            }
        },
        "position": [-444.37109375, -24.49609375],
        "name": "Start",
    }

    start_model = StartModel(**input_data)

    assert start_model.dict(by_alias=True) == {
        "id": "0",
        "outputs": {
            "output_void": {
                "connections": [
                    {"node": "3", "input": "input_void"},
                    {"node": "4", "input": "input_void"},
                ]
            }
        },
    }
