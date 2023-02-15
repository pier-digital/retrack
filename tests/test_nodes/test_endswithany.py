import pandas as pd

from retrack.nodes.endswithany import EndsWithAny

input_data = {
    "id": 13,
    "data": {},
    "inputs": {"input_value": {"connections": []}, "input_list": {"connections": []}},
    "outputs": {"output_bool": {"connections": []}},
    "position": [1178.650051545976, 855.8644837700068],
    "name": "EndsWithAny",
}


def test_EndsWithAny_node():
    EndsWithAny_node = EndsWithAny(**input_data)

    assert isinstance(EndsWithAny_node, EndsWithAny)

    assert EndsWithAny_node.dict(by_alias=True) == {
        "id": "13",
        "inputs": {
            "input_value": {"connections": []},
            "input_list": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
    }


def test_EndsWithAny_node_run():

    EndsWithAny_node = EndsWithAny(**input_data)

    output = EndsWithAny_node.run(pd.Series(["100"]), pd.Series(["2", "1"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = EndsWithAny_node.run(pd.Series(["100"]), pd.Series(["2", "0"]))
    assert (output["output_bool"] == pd.Series([True])).all()
