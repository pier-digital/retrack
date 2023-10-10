import pandas as pd

from retrack.nodes.startswithany import StartsWithAny

input_data = {
    "id": 13,
    "data": {},
    "inputs": {"input_value": {"connections": []}, "input_list": {"connections": []}},
    "outputs": {"output_bool": {"connections": []}},
    "position": [1178.650051545976, 855.8644837700068],
    "name": "StartsWithAny",
}


def test_StartsWithAny_node():
    StartsWithAny_node = StartsWithAny(**input_data)

    assert isinstance(StartsWithAny_node, StartsWithAny)

    assert StartsWithAny_node.model_dump(by_alias=True) == {
        "id": "13",
        "inputs": {
            "input_value": {"connections": []},
            "input_list": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
    }


def test_StartsWithAny_node_run():
    StartsWithAny_node = StartsWithAny(**input_data)

    output = StartsWithAny_node.run(pd.Series(["100"]), pd.Series(["2", "1"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = StartsWithAny_node.run(pd.Series(["100"]), pd.Series(["2", "3"]))
    assert (output["output_bool"] == pd.Series([False])).all()
