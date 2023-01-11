import pandas as pd

from retack.nodes.endswith import EndsWith

input_data = {
    "id": 11,
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
		1277.7969569337479,
		537.1240779622773
	],
	"name": "EndsWith"
}

def test_EndsWith_node():
    EndsWith_node = EndsWith(**input_data)

    assert isinstance(EndsWith_node, EndsWith)

    assert EndsWith_node.dict(by_alias=True) == {
        "id": "10",
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
    }


def test_EndsWith_node_run():

    EndsWith_node = EndsWith(**input_data)
    output = EndsWith_node.run(pd.Series(["100"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([False])).all()