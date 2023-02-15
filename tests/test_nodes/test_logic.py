import pandas as pd

from retrack.nodes.logic import And, Not, Or

input_data_And = {
    "id": 15,
    "data": {},
    "inputs": {
        "input_bool_0": {"connections": []},
        "input_bool_1": {"connections": []},
    },
    "outputs": {"output_bool": {"connections": []}},
    "position": [600.2264533807651, 1113.094677616452],
    "name": "And",
}

input_data_Or = {
    "id": 16,
    "data": {},
    "inputs": {
        "input_bool_0": {"connections": []},
        "input_bool_1": {"connections": []},
    },
    "outputs": {"output_bool": {"connections": []}},
    "position": [891.9762574619829, 1017.9278275583388],
    "name": "Or",
}

input_data_Not = {
    "id": 17,
    "data": {},
    "inputs": {"input_bool": {"connections": []}},
    "outputs": {"output_bool": {"connections": []}},
    "position": [1195.5017776430686, 1080.1383409685295],
    "name": "Not",
}


def test_Logic_node():
    And_node = And(**input_data_And)
    Or_node = Or(**input_data_Or)
    Not_node = Not(**input_data_Not)

    assert isinstance(And_node, And)
    assert isinstance(Or_node, Or)
    assert isinstance(Not_node, Not)

    assert And_node.dict(by_alias=True) == {
        "id": "15",
        "inputs": {
            "input_bool_0": {"connections": []},
            "input_bool_1": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
    }


def test_And_node_run():
    And_node = And(**input_data_And)
    Or_node = Or(**input_data_Or)
    Not_node = Not(**input_data_Not)

    output = And_node.run(pd.Series([True]), pd.Series([False]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = And_node.run(pd.Series([False]), pd.Series([True]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = And_node.run(pd.Series([False]), pd.Series([False]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = And_node.run(pd.Series([True]), pd.Series([True]))
    assert (output["output_bool"] == pd.Series([True])).all()

    output = Or_node.run(pd.Series([True]), pd.Series([False]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = Or_node.run(pd.Series([True]), pd.Series([True]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = Or_node.run(pd.Series([False]), pd.Series([True]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = Or_node.run(pd.Series([False]), pd.Series([False]))
    assert (output["output_bool"] == pd.Series([False])).all()

    output = Not_node.run(pd.Series([True]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = Not_node.run(pd.Series([False]))
    assert (output["output_bool"] == pd.Series([True])).all()
