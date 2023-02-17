import pydantic

from retrack.nodes.base import BaseNode, NodeKind, OutputConnectionModel

################################################
# Start Inputs and Outputs
################################################


class StartOutputsModel(pydantic.BaseModel):
    output_up_void: OutputConnectionModel
    output_down_void: OutputConnectionModel


################################################
# Start Node
################################################


class Start(BaseNode):
    outputs: StartOutputsModel

    def kind(self) -> NodeKind:
        return NodeKind.START
