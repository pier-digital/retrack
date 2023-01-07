import pydantic

from retack.models.base import ComponentModel, OutputConnectionModel


class StartOutputsModel(pydantic.BaseModel):
    output_up_void: OutputConnectionModel
    output_down_void: OutputConnectionModel


class StartModel(ComponentModel):
    outputs: StartOutputsModel
