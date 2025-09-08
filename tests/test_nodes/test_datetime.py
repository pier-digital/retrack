import pytest

from retrack.nodes.datetime import CurrentYear


@pytest.fixture
def current_year_input_data():
    return {
        "id": 18,
        "data": {},
        "inputs": {
            "input_void": {"connections": []},
        },
        "outputs": {"output_value": {"connections": []}},
        "position": [251.88962048090218, 1013.6680559036622],
        "name": "CurrentYear",
    }


def test_current_year_node(current_year_input_data):
    current_year_node = CurrentYear(**current_year_input_data)

    assert isinstance(current_year_node, CurrentYear)


@pytest.mark.asyncio
async def test_current_year_node_run(current_year_input_data, mocker):
    datetime_mock = mocker.patch("retrack.nodes.datetime.dt.datetime")
    datetime_mock.now.return_value = mocker.MagicMock(year=2021)
    current_year_node = CurrentYear(**current_year_input_data)
    output = await current_year_node.run()
    assert output["output_value"] == 2021
