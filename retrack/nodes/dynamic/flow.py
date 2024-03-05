import json
import typing

import pandas as pd
import pydantic

from retrack.nodes.base import InputConnectionModel, NodeKind, OutputConnectionModel
from retrack.nodes.dynamic.base import BaseDynamicIOModel, BaseDynamicNode
from retrack.utils.registry import Registry


class FlowV0MetadataModel(pydantic.BaseModel):
    value: str
    name: typing.Optional[str] = None
    default: typing.Optional[str] = None

    def parsed_value(self) -> typing.Dict[str, typing.Any]:
        return json.loads(self.value)


class FlowV0OutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


def flow_factory(
    inputs: typing.Dict[str, typing.Any],
    nodes_registry: Registry,
    dynamic_nodes_registry: Registry,
    validator_registry: Registry,
    data: dict,
    rule_class,
    **factory_kwargs,
) -> typing.Type[BaseDynamicNode]:
    graph_data = json.loads(data["value"])
    rule_instance = rule_class.create(
        graph_data=graph_data,
        nodes_registry=nodes_registry,
        dynamic_nodes_registry=dynamic_nodes_registry,
        validator_registry=validator_registry,
        name=data["name"],
    )
    input_fields = {}

    for name in inputs.keys():
        input_fields[name] = BaseDynamicNode.create_sub_field(InputConnectionModel)

    inputs_model = BaseDynamicIOModel.with_fields("FlowV0InputsModel", **input_fields)

    models = {
        "inputs": BaseDynamicNode.create_sub_field(inputs_model),
        "outputs": BaseDynamicNode.create_sub_field(FlowV0OutputsModel),
        "data": BaseDynamicNode.create_sub_field(FlowV0MetadataModel),
    }

    BaseFlowV0Model = BaseDynamicNode.with_fields("FlowV0", **models)

    class FlowV0(BaseFlowV0Model):
        def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
            input_args = {}
            for name, value in kwargs.items():
                if name.startswith("input_"):
                    name = name[len("input_") :]

                input_args[name] = value

            response = rule_instance.executor.execute(pd.DataFrame(input_args))

            return {"output_value": response["output"].values}

        def generate_input_nodes(self):
            input_nodes = []
            for component in rule_instance.components_registry.data.values():
                input_nodes.extend(component.generate_input_nodes())
            return input_nodes

        def kind(self) -> NodeKind:
            return NodeKind.FLOW

    return FlowV0
