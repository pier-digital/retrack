import typing

from retrack.nodes.base import NodeKind
import pydantic

from retrack.nodes.base import InputConnectionModel, OutputConnectionModel
from retrack.nodes.dynamic.base import BaseDynamicIOModel, BaseDynamicNode
from retrack.utils import constants


class FlowConnectorMetadataModel(pydantic.BaseModel):
    name: str
    flow: str
    version: str
    default: typing.Optional[str] = None


def connector_header(connector_name: str) -> str:
    """Return the child output header for a FlowConnector output connector.

    The editor names each output connector ``{header}@{child_node_id}`` so the
    keys stay unique. The child flow returns items keyed by the bare header.
    """
    return connector_name.split("@", 1)[0]


def flow_connector_factory(
    inputs: typing.Dict[str, typing.Any], **kwargs
) -> typing.Type[BaseDynamicNode]:
    input_fields = {}

    for name in inputs.keys():
        input_fields[name] = BaseDynamicNode.create_sub_field(InputConnectionModel)

    inputs_model = BaseDynamicIOModel.with_fields(
        "FlowConnectorInputsModel", **input_fields
    )

    output_connectors = list((kwargs.get("outputs") or {}).keys()) or [
        constants.INPUT_OUTPUT_VALUE_CONNECTOR_NAME
    ]
    is_multi_output = output_connectors != [
        constants.INPUT_OUTPUT_VALUE_CONNECTOR_NAME
    ]

    outputs_model = BaseDynamicIOModel.with_fields(
        "FlowConnectorOutputsModel",
        **{
            name: BaseDynamicNode.create_sub_field(OutputConnectionModel)
            for name in output_connectors
        },
    )

    models = {
        "inputs": BaseDynamicNode.create_sub_field(inputs_model),
        "outputs": BaseDynamicNode.create_sub_field(outputs_model),
        "data": BaseDynamicNode.create_sub_field(FlowConnectorMetadataModel),
    }

    BaseModel = BaseDynamicNode.with_fields("FlowConnectorBaseModel", **models)

    class FlowConnector(BaseModel):
        def kind(self) -> NodeKind:
            return NodeKind.CONNECTOR

        def payload_columns(self) -> typing.Dict[str, str]:
            if not is_multi_output:
                return super().payload_columns()

            return {
                name: f"{self.data.name}.{connector_header(name)}"
                for name in output_connectors
            }

        async def run(self, **kwargs):
            return {}

    return FlowConnector
