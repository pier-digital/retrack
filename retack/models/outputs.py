import typing

import pydantic

from retack.models.base import InputConnectionModel


class BoolOutputInputsModel(pydantic.BaseModel):
    input_bool: InputConnectionModel


class BoolOutputModel(pydantic.BaseModel):
    id: str
    inputs: typing.Optional[BoolOutputInputsModel]
