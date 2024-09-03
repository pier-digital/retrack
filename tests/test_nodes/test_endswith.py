import pandas as pd

from retrack.nodes.endswith import EndsWith

input_data = {
    "id": 11,
    "data": {},
    "inputs": {
        "input_value_0": {"connections": []},
        "input_value_1": {"connections": []},
    },
    "outputs": {"output_bool": {"connections": []}},
    "position": [1277.7969569337479, 537.1240779622773],
    "name": "EndsWith",
}


def test_ends_with_node():
    ends_with_node = EndsWith(**input_data)

    assert isinstance(ends_with_node, EndsWith)


def test_ends_with_node_run():
    ends_with_node = EndsWith(**input_data)

    output = ends_with_node.run(pd.Series(["100"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = ends_with_node.run(pd.Series(["102"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([True])).all()
