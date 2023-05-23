import typing

import pydantic

from retrack.nodes.base import BaseNode


class BaseDynamicIOModel(pydantic.BaseModel):
    @classmethod
    def with_fields(cls, class_name: str, **field_definitions):
        return pydantic.create_model(
            class_name, __base__=BaseDynamicIOModel, **field_definitions
        )


class BaseDynamicNode(BaseNode):
    @classmethod
    def with_fields(cls, class_name: str, **field_definitions):
        return pydantic.create_model(class_name, __base__=BaseNode, **field_definitions)

    @staticmethod
    def create_sub_field(
        type_: typing.Any, optional: bool = False, default_value: typing.Any = None
    ) -> typing.Tuple[typing.Type, typing.Any]:
        if optional:
            return (typing.Optional[type_], default_value)

        return (type_, ...)
