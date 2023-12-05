import pytest
import pandas as pd
from retrack import from_json, BaseConnector, nodes_registry
from retrack.nodes.inputs import Input
import pandera as pa


@pytest.fixture
def custom_connector():
    class MyConnector(BaseConnector):
        def run(self, feature_a: pd.Series, feature_b: pd.Series, **kwargs):
            return {"output_value": feature_a.astype(float) + feature_b.astype(float)}

        def generate_input_nodes(self):
            base_dict = self.model_dump(by_alias=True)
            inputs = []
            for feature_name in ["feature_a", "feature_b"]:
                base_dict["id"] = self.id + "_" + feature_name
                base_dict["data"]["name"] = feature_name
                inputs.append(Input(**base_dict))

            return inputs

    return MyConnector


@pytest.mark.parametrize(
    "filename, in_values, expected_out_values",
    [
        (
            "connector-rule",
            [
                {"feature_a": "1", "feature_b": "4", "multiplier": "1"},
                {"feature_a": "2", "feature_b": "1", "multiplier": "1"},
                {"feature_a": "3", "feature_b": "3", "multiplier": "1"},
                {"feature_a": "4", "feature_b": "0", "multiplier": "1"},
            ],
            [
                {"output": 5.0, "message": None},
                {"output": 3.0, "message": None},
                {"output": 6.0, "message": None},
                {"output": 4.0, "message": None},
            ],
        ),
        (
            "rule-of-rules-with-connector",
            [
                {"feature_a": "1", "feature_b": "4", "var": "1"},
                {"feature_a": "2", "feature_b": "1", "var": "1"},
                {"feature_a": "3", "feature_b": "3", "var": "1"},
                {"feature_a": "4", "feature_b": "0", "var": "1"},
            ],
            [
                {"output": 5.0, "message": None},
                {"output": 3.0, "message": None},
                {"output": 6.0, "message": None},
                {"output": 4.0, "message": None},
            ],
        ),
    ],
)
def test_connectors_with_custom_code(
    filename, in_values, expected_out_values, custom_connector
):
    custom_registry = nodes_registry()
    custom_registry.register("Connector", custom_connector, overwrite=True)
    custom_registry.register("ConnectorV0", custom_connector, overwrite=True)

    runner = from_json(
        f"tests/resources/{filename}.json", nodes_registry=custom_registry
    )
    out_values = runner.execute(pd.DataFrame(in_values))

    assert isinstance(out_values, pd.DataFrame)
    assert out_values.to_dict(orient="records") == expected_out_values


def test_missing_input_for_custom_connectors(custom_connector):
    custom_registry = nodes_registry()
    custom_registry.register("Connector", custom_connector, overwrite=True)
    custom_registry.register("ConnectorV0", custom_connector, overwrite=True)

    with pytest.raises(pa.errors.SchemaError):
        runner = from_json(
            "tests/resources/connector-rule.json",
            nodes_registry=custom_registry,
        )

        runner.execute(pd.DataFrame([{"multiplier": "1", "prediction": "4"}]))
