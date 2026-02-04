import typing

from retrack.nodes.base import NodeKind
import pydantic

from retrack.nodes.base import InputConnectionModel, OutputConnectionModel
from retrack.nodes.dynamic.base import BaseDynamicIOModel, BaseDynamicNode


class FlowConnectorMetadataModel(pydantic.BaseModel):
    name: str
    rule: str
    version: str
    default: typing.Optional[str] = None


class FlowConnectorOutputModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


def flow_connector_factory(
    inputs: typing.Dict[str, typing.Any], **kwargs
) -> typing.Type[BaseDynamicNode]:
    input_fields = {}

    for name in inputs.keys():
        input_fields[name] = BaseDynamicNode.create_sub_field(InputConnectionModel)

    inputs_model = BaseDynamicIOModel.with_fields(
        "FlowConnectorInputsModel", **input_fields
    )

    models = {
        "inputs": BaseDynamicNode.create_sub_field(inputs_model),
        "outputs": BaseDynamicNode.create_sub_field(FlowConnectorOutputsModel),
        "data": BaseDynamicNode.create_sub_field(FlowConnectorMetadataModel),
    }

    BaseModel = BaseDynamicNode.with_fields("FlowConnectorBaseModel", **models)

    class FlowConnector(BaseModel):
        def kind(self) -> NodeKind:
            return NodeKind.CONNECTOR

        async def run(self, **kwargs):
            return {}

    return FlowConnector
