import typing

from retrack.nodes.base import NodeKind
import pydantic

from retrack.nodes.base import InputConnectionModel, OutputConnectionModel
from retrack.nodes.dynamic.base import BaseDynamicIOModel, BaseDynamicNode


class ConditionalConnectorMetadataModel(pydantic.BaseModel):
    name: str
    source: str
    resource: str
    default: typing.Optional[str] = None
    headers: typing.List[str]
    headers_map: typing.List[str]


class ConditionalConnectorOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


def conditional_connector_factory(
    inputs: typing.Dict[str, typing.Any], **kwargs
) -> typing.Type[BaseDynamicNode]:
    input_fields = {}

    for name in inputs.keys():
        input_fields[name] = BaseDynamicNode.create_sub_field(InputConnectionModel)

    inputs_model = BaseDynamicIOModel.with_fields(
        "ConditionalConnectorInputsModel", **input_fields
    )

    models = {
        "inputs": BaseDynamicNode.create_sub_field(inputs_model),
        "outputs": BaseDynamicNode.create_sub_field(ConditionalConnectorOutputsModel),
        "data": BaseDynamicNode.create_sub_field(ConditionalConnectorMetadataModel),
    }

    BaseModel = BaseDynamicNode.with_fields("ConditionalConnectorBaseModel", **models)

    class ConditionalConnector(BaseModel):
        def kind(self) -> NodeKind:
            return NodeKind.CONNECTOR

        def run(self, **kwargs):
            return {}

    return ConditionalConnector
