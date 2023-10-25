import typing

import json

import pandas as pd
import pydantic

from retrack.nodes.base import InputConnectionModel, OutputConnectionModel
from retrack.nodes.dynamic.base import BaseDynamicIOModel, BaseDynamicNode


class FlowV0MetadataModel(pydantic.BaseModel):
    value: str
    name: typing.Optional[str] = None
    default: typing.Optional[str] = None

    def parsed_value(self) -> typing.Dict[str, typing.Any]:
        return json.loads(self.value)


class FlowV0OutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


def flow_factory(
    inputs: typing.Dict[str, typing.Any], **kwargs
) -> typing.Type[BaseDynamicNode]:
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
            runner = kwargs.get("runner", None)
            if runner is None:
                raise ValueError("Missing runner")

            inputs_in_kwargs = {}

            for name, value in kwargs.items():
                if name.startswith("input_"):
                    inputs_in_kwargs[name[6:]] = value

            response = runner.execute(pd.DataFrame(inputs_in_kwargs))

            return {"output_value": response["output"].values}

    return FlowV0
