import pandas as pd
import pytest

from retrack.nodes.check import Check, CheckOperator


@pytest.fixture
def node_schema():
    return {
        "id": 8,
        "data": {"operator": "=="},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
        "position": [-6.535670037902264, 838.4506094490812],
        "name": "Check",
    }


def test_check_node(node_schema):
    check_node = Check(**node_schema)

    assert isinstance(check_node, Check)
    assert isinstance(check_node.data.operator, CheckOperator)

    assert check_node.dict(by_alias=True) == {
        "id": "8",
        "data": {"operator": CheckOperator.EQUAL},
        "inputs": {
            "input_value_0": {"connections": []},
            "input_value_1": {"connections": []},
        },
        "outputs": {"output_bool": {"connections": []}},
    }


def test_check_equals_node_run(node_schema):
    node_schema["data"]["operator"] = "=="
    check_node = Check(**node_schema)

    output = check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = check_node.run(pd.Series(["True"]), pd.Series([True]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = check_node.run(pd.Series(["False"]), pd.Series([False]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = check_node.run(pd.Series(["False"]), pd.Series([True]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = check_node.run(pd.Series([1.23]), pd.Series([1.23]))
    assert (output["output_bool"] == pd.Series([True])).all()


def test_check_not_equals_node_run(node_schema):
    node_schema["data"]["operator"] = "!="
    check_node = Check(**node_schema)

    output = check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([True])).all()


def test_check_greater_than_node_run(node_schema):
    node_schema["data"]["operator"] = ">"
    check_node = Check(**node_schema)

    output = check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = check_node.run(pd.Series(["2"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([True])).all()


def test_check_less_than_node_run(node_schema):
    node_schema["data"]["operator"] = "<"
    check_node = Check(**node_schema)

    output = check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = check_node.run(pd.Series(["2"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([False])).all()


def test_check_greater_than_or_equal_node_run(node_schema):
    node_schema["data"]["operator"] = ">="
    check_node = Check(**node_schema)

    output = check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = check_node.run(pd.Series(["2"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([True])).all()


def test_check_less_than_or_equal_node_run(node_schema):
    node_schema["data"]["operator"] = "<="
    check_node = Check(**node_schema)

    output = check_node.run(pd.Series(["1"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = check_node.run(pd.Series(["1"]), pd.Series(["2"]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = check_node.run(pd.Series(["2"]), pd.Series(["1"]))
    assert (output["output_bool"] == pd.Series([False])).all()
