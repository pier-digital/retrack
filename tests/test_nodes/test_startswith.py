import pandas as pd

from retack.nodes.startswith import StartsWith

input_data = {
	"id": 10,
	"data": {},
	"inputs": {
		"input_value_0": {
			"connections": []
		},
		"input_value_1": {
			"connections": []
		}
	},
	"outputs": {
		"output_bool": {
			"connections": []
		}
	},
	"position": [
		1321.9899743354695,
		255.18171516041082
	],
	"name": "StartsWith"
}

def test_StartsWith_node():
    StartsWith_node = StartsWith(**input_data)

    assert isinstance(StartsWith_node, StartsWith)

    assert StartsWith_node.dict(by_alias=True) == {
        "id": "10",
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
    }


def test_StartsWith_node_run():

    StartsWith_node = StartsWith(**input_data)
    output = StartsWith_node.run(pd.Series(["100"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([False])).all()