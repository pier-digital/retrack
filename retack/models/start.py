import pydantic

from retack.models.base import OutputConnectionModel


class StartOutputsModel(pydantic.BaseModel):
    output_void: OutputConnectionModel


class StartModel(pydantic.BaseModel):
    id: str
    outputs: StartOutputsModel
