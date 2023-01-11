import pandas as pd

from retack.nodes.contains import Contains

input_data = {
    "id": 9,
	"data": {},
	"inputs": {
		"input_list": {
			"connections": []
		},
		"input_value": {
			"connections": []
		}
	},
	"outputs": {
		"output_bool": {
			"connections": []
		}
	},
	"position": [
		1597.1904571362154,
		628.6495284260166
	],
	"name": "Contains"
}

def test_Contains_node():
    Contains_node = Contains(**input_data)

    assert isinstance(Contains_node, Contains)

    assert Contains_node.dict(by_alias=True) == {
        "id": "9",
        "inputs": {
            "input_list": {"connections": []},
            "input_value": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
    }


def test_Contains_node_run():

    Contains_node = Contains(**input_data)
    output = Contains_node.run(pd.Series(["1", "2"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([True])).all()
