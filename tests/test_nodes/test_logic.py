import pandas as pd

from retrack.nodes.logic import And, Not, Or
import pytest


@pytest.fixture
def input_data_and():
    return {
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


@pytest.fixture
def input_data_or():
    return {
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


@pytest.fixture
def input_data_not():
    return {
        "id": 17,
        "data": {},
        "inputs": {"input_bool": {"connections": []}},
        "outputs": {"output_bool": {"connections": []}},
        "position": [1195.5017776430686, 1080.1383409685295],
        "name": "Not",
    }


def test_logic_node(input_data_and, input_data_or, input_data_not):
    and_node = And(**input_data_and)
    or_node = Or(**input_data_or)
    not_node = Not(**input_data_not)

    assert isinstance(and_node, And)
    assert isinstance(or_node, Or)
    assert isinstance(not_node, Not)


@pytest.mark.asyncio
async def test_and_node_run(input_data_and, input_data_or, input_data_not):
    and_node = And(**input_data_and)
    or_node = Or(**input_data_or)
    not_node = Not(**input_data_not)

    output = await and_node.run(pd.Series([True]), pd.Series([False]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = await and_node.run(pd.Series([False]), pd.Series([True]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = await and_node.run(pd.Series([False]), pd.Series([False]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = await and_node.run(pd.Series([True]), pd.Series([True]))
    assert (output["output_bool"] == pd.Series([True])).all()

    output = await or_node.run(pd.Series([True]), pd.Series([False]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = await or_node.run(pd.Series([True]), pd.Series([True]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = await or_node.run(pd.Series([False]), pd.Series([True]))
    assert (output["output_bool"] == pd.Series([True])).all()
    output = await or_node.run(pd.Series([False]), pd.Series([False]))
    assert (output["output_bool"] == pd.Series([False])).all()

    output = await not_node.run(pd.Series([True]))
    assert (output["output_bool"] == pd.Series([False])).all()
    output = await not_node.run(pd.Series([False]))
    assert (output["output_bool"] == pd.Series([True])).all()
