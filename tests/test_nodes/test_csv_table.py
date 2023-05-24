import pandas as pd
import pydantic
import pytest

from retrack.nodes import dynamic_registry


@pytest.fixture
def csv_table_metadata():
    return {
        "id": 2,
        "data": {
            "separator": ",",
            "value": [
                "month,first_year,second_year,third_year",
                "JAN,340,360,417",
                "FEB,318,342,391",
                "MAR,362,406,419",
                "APR,348,396,461",
                "MAY,363,420,472",
                "JUN,435,472,535",
                "JUL,491,548,622",
                "AUG,505,559,606",
                "SEP,404,463,508",
                "OCT,359,407,461",
                "NOV,310,362,390",
                "DEC,337,405,432",
            ],
            "default": "200",
            "headers": ["month", "first_year", "second_year", "third_year"],
            "target": "output_value",
            "headers_map": [
                "input_value_0",
                "input_value_1",
                "input_value_2",
                "output_value",
            ],
        },
        "inputs": {
            "input_value_0": {
                "connections": [{"node": 4, "output": "output_value", "data": {}}]
            },
            "input_value_1": {
                "connections": [{"node": 5, "output": "output_value", "data": {}}]
            },
            "input_value_2": {
                "connections": [{"node": 6, "output": "output_value", "data": {}}]
            },
        },
        "outputs": {
            "output_value": {
                "connections": [
                    {"node": 7, "input": "input_void", "data": {}},
                    {"node": 8, "input": "input_value_0", "data": {}},
                ]
            }
        },
        "name": "CSVTableV0",
    }


def test_get_csv_table_factory():
    csv_table_factory = dynamic_registry().get("CSVTableV0")

    assert callable(csv_table_factory)


def test_create_model_from_factory(csv_table_metadata):
    csv_table_factory = dynamic_registry().get("CSVTableV0")
    CSVTableV0 = csv_table_factory(**csv_table_metadata)

    assert issubclass(CSVTableV0, pydantic.BaseModel)

    model = CSVTableV0(**csv_table_metadata)

    assert isinstance(model, CSVTableV0)
    assert hasattr(model, "run")


def test_csv_table_run(csv_table_metadata):
    csv_table_factory = dynamic_registry().get("CSVTableV0")
    CSVTableV0 = csv_table_factory(**csv_table_metadata)

    model = CSVTableV0(**csv_table_metadata)

    payload = {
        "input_value_0": pd.Series(["MAY", "JUN", "JUL", "AUG", "SEP"]),
        "input_value_1": pd.Series(["363", "435", "491", "505", "-1"]),
        "input_value_2": pd.Series(["420", "472", "548", "559", "463"]),
    }

    expected = pd.Series(["472", "535", "622", "606", model.data.default])

    response = model.run(**payload)
    assert response["output_value"].equals(expected)
