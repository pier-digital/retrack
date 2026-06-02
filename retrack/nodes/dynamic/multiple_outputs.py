import typing

import pandas as pd
import pydantic

from retrack.nodes.base import InputConnectionModel, NodeKind, OptionalCastedToNoneStringType
from retrack.nodes.dynamic.base import BaseDynamicIOModel, BaseDynamicNode
from retrack.utils import constants


class MultipleOutputsMetadataModel(pydantic.BaseModel):
    headers_map: typing.List[str]
    message: OptionalCastedToNoneStringType = None
    name: typing.Optional[str] = None

    @pydantic.field_validator("headers_map")
    @classmethod
    def validate_headers_map(cls, v: typing.List[str]) -> typing.List[str]:
        if not v:
            raise ValueError("headers_map must not be empty")
        if len(v) != len(set(v)):
            raise ValueError("headers_map must not contain duplicate keys")
        return v


def multiple_outputs_factory(
    inputs: typing.Dict[str, typing.Any], **kwargs
) -> typing.Type[BaseDynamicNode]:
    input_fields = {
        name: BaseDynamicNode.create_sub_field(InputConnectionModel)
        for name in inputs.keys()
    }
    inputs_model = BaseDynamicIOModel.with_fields(
        "MultipleOutputsInputsModel", **input_fields
    )

    models = {
        "inputs": BaseDynamicNode.create_sub_field(inputs_model),
        "data": BaseDynamicNode.create_sub_field(MultipleOutputsMetadataModel),
    }

    BaseModel = BaseDynamicNode.with_fields("MultipleOutputsBaseModel", **models)

    class MultipleOutputs(BaseModel):
        def kind(self) -> NodeKind:
            return NodeKind.OUTPUT

        async def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
            keys = self.data.headers_map
            rows = zip(*[kwargs[k].values for k in keys])
            output_series = pd.Series(
                [[{"key": k, "value": v} for k, v in zip(keys, row)] for row in rows],
                index=kwargs[keys[0]].index,
                dtype=object,
            )
            return {
                constants.OUTPUT_REFERENCE_COLUMN: output_series,
                constants.OUTPUT_MESSAGE_REFERENCE_COLUMN: self.data.message,
            }

    return MultipleOutputs
