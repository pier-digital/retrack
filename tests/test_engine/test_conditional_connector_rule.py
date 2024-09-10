import typing
import retrack
from retrack.nodes.dynamic import BaseDynamicNode, Registry
from retrack.nodes.dynamic import registry as dynamic_nodes_registry_factory
from retrack.nodes.dynamic.conditional_connector import conditional_connector_factory
import pandas as pd
import pytest

VALUES = {"qtd_sinistros_rcf": 1, "qtd_sinistros_indefinido": 10, "is_defendant_and_court_type": False}


def bureau_connector_factory(
    inputs: typing.Dict[str, typing.Any], **kwargs
) -> typing.Type[BaseDynamicNode]:
    node_class = conditional_connector_factory(inputs=inputs, **kwargs)

    class ExampleConditionalConnectorNode(node_class):
        def run(
            self, context: typing.Optional[Registry] = None, **node_inputs
        ) -> typing.Dict[str, typing.Any]:
            parsed_inputs = {}
            for i, in_node_key in enumerate(self.data.headers_map):
                if in_node_key not in node_inputs.keys():
                    raise ValueError(
                        f"Missing input {in_node_key} in BureauConnector node"
                    )
                
                if node_inputs[in_node_key].empty:
                    return {"output_value": None}

                parsed_inputs[self.data.headers[i]] = node_inputs[in_node_key].to_list()[0]

            return {"output_value": VALUES[self.data.resource]}

    return ExampleConditionalConnectorNode


@pytest.mark.parametrize(
    "age, cpf, license_plate, expected_result, expected_message",
    [
        (40, "12345678900", "ABC1234", 11, "rns"),
        (17, "12345678900", "ABC1234", False, "bdc"),
    ],
)
def test_bureau_connector_factory(
    age, cpf, license_plate, expected_result, expected_message
):
    dynamic_nodes_registry = dynamic_nodes_registry_factory()
    dynamic_nodes_registry.register(
        "BureauConnector", bureau_connector_factory, overwrite=True
    )
    rule_executor = retrack.from_json(
        "tests/resources/conditional-connector.json",
        dynamic_nodes_registry=dynamic_nodes_registry,
        return_executor=True,
        raise_if_null_version=False,
        validate_version=False,
    )

    input_nodes = rule_executor.components_registry.get_by_kind(
        retrack.nodes.base.NodeKind.INPUT
    )
    input_nodes.extend(rule_executor.components_registry.get_by_name("connectorv0"))

    rule_executor.reset_request_manager(input_nodes)

    df = pd.DataFrame({"age": [age], "cpf": [cpf], "license_plate": [license_plate]})

    result = rule_executor.execute(df, raise_raw_exception=True)
    assert result["output"].to_list()[0] == expected_result
    assert result["message"].to_list()[0] == expected_message