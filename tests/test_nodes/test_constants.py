from retrack.nodes.constants import IntervalCatV0
import pytest
import pandas as pd


@pytest.fixture
def interval_cat_dict():
    return {
        "id": "75e8a620332cbe6b",
        "name": "IntervalCatV0",
        "data": {
            "value": [
                "score_minimo,score_maximo,score_cat",
                "-inf,451,0",
                "451,1001,{value}",
                "1001,inf,1000",
            ],
            "default": "-1",
            "start_interval_column": "score_minimo",
            "end_interval_column": "score_maximo",
            "category_column": "score_cat",
            "headers": ["score_minimo", "score_maximo", "score_cat"],
            "separator": ",",
        },
        "outputs": {
            "output_value": {
                "connections": [{"node": "7fd9c8e881cefa54", "input": "input_value"}]
            }
        },
        "inputs": {
            "input_value": {
                "connections": [{"node": "a3191764d4772466", "output": "output_value"}]
            }
        },
    }


def test_interval_cat_v0(interval_cat_dict):
    interval_cat = IntervalCatV0(**interval_cat_dict)

    assert isinstance(interval_cat, IntervalCatV0)
    assert hasattr(interval_cat, "run")


@pytest.mark.asyncio
async def test_interval_cat_v0_run(interval_cat_dict):
    interval_cat = IntervalCatV0(**interval_cat_dict)

    input_series = pd.Series([-1000, 1, 450, 451, 900, 1001, 320000])
    output = await interval_cat.run(input_value=input_series)

    expected_output = pd.Series([0, 0, 0, 451, 900, 1000, 1000])
    assert (output["output_value"].astype(str) == expected_output.astype(str)).all()
