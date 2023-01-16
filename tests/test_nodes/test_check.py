import pandas as pd

from retrack.nodes.check import Check, CheckOperator

input_data = {
        "id": 8,
		"data": {
			"operator": "=="
		},
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
			-6.535670037902264,
			838.4506094490812
		],
		"name": "Check"
    }

def test_Check_node():

    Check_node = Check(**input_data)

    assert isinstance(Check_node, Check)
    assert isinstance(Check_node.data.operator, CheckOperator)

    assert Check_node.dict(by_alias=True) == {
        "id": "8",
        "data": {"operator": CheckOperator.EQUAL},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
    }


def test_Check_node_run():

    Check_node = Check(**input_data)

    output = Check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = Check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([False])).all()

    input_data['data']['operator'] = '!='
    Check_node = Check(**input_data)

    output = Check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = Check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([True])).all()

    input_data['data']['operator'] = '>'
    Check_node = Check(**input_data)

    output = Check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = Check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = Check_node.run(pd.Series(["2"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([True])).all()

    input_data['data']['operator'] = '<'
    Check_node = Check(**input_data)

    output = Check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = Check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = Check_node.run(pd.Series(["2"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([False])).all()

    input_data['data']['operator'] = '>='
    Check_node = Check(**input_data)
    
    output = Check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = Check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = Check_node.run(pd.Series(["2"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([True])).all()

    input_data['data']['operator'] = '<='
    Check_node = Check(**input_data)

    output = Check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = Check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = Check_node.run(pd.Series(["2"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([False])).all()