import pydantic
import typing


class RuleMetadata(pydantic.BaseModel):
    name: typing.Optional[str] = pydantic.Field(
        None, description="The name of the rule"
    )
    version: str = pydantic.Field(..., description="The version of the rule")


class ExecutionSchema(pydantic.BaseModel):
    payload: typing.Any = pydantic.Field(
        ..., description="The payload of the execution"
    )
    states: typing.Any = pydantic.Field(
        ..., description="The states of the execution"
    )
    filters: typing.Dict[str, typing.Any] = pydantic.Field(
        ..., description="The filters of the execution"
    )
    result: typing.Any = pydantic.Field(
        ..., description="The result of the execution"
    )
    has_ended: bool = pydantic.Field(
        ..., description="If the execution has ended"
    )


class ExecutionMetadata(RuleMetadata):
    node_id: typing.Optional[str] = pydantic.Field(None, description="The node id")
    execution: typing.Optional[ExecutionSchema] = pydantic.Field(None, description="Metadata of the rule execution")


class ExceptionSchema(pydantic.BaseModel):
    msg: str = pydantic.Field(..., description="The exception message")
    exception_type: str = pydantic.Field(..., description="The exception type")
    traceback: typing.Any = pydantic.Field(..., description="The exception traceback")


class DetailSchema(pydantic.BaseModel):
    msg: str = pydantic.Field(
        ...,
        description="A human-readable explanation specific to this occurrence of the problem. This field’s value can be localized",
    )
    type_: str = pydantic.Field(
        ..., alias="type", description="The type of the problem"
    )
    exception: ExceptionSchema = pydantic.Field(
        ..., description="The exception that caused the problem"
    )


class ErrorSchema(pydantic.BaseModel):
    title: str = pydantic.Field(
        ...,
        description="A short, human-readable summary of the problem that SHOULD NOT change from occurrence to occurrence of the problem",
    )
    detail: DetailSchema = pydantic.Field(
        ...,
        description="A explanation specific to this occurrence of the problem. This field’s value can be localized",
    )
    status: str = pydantic.Field(
        ...,
        description="The HTTP status code applicable to this problem, expressed as a string value",
    )
    metadata: ExecutionMetadata = pydantic.Field(
        ..., description="Rule metadata"
    )
