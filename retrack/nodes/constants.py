import typing

import numpy as np
import pandas as pd
import pydantic

from retrack.nodes.base import (
    BaseNode,
    InputConnectionModel,
    NodeKind,
    NodeMemoryType,
    OutputConnectionModel,
)

#######################################################
# Constant Metadata Models
#######################################################


class ConstantMetadataModel(pydantic.BaseModel):
    value: str


class ListMetadataModel(pydantic.BaseModel):
    value: typing.List[str]


class BoolMetadataModel(pydantic.BaseModel):
    value: typing.Optional[bool] = pydantic.Field(False, alias="value")

    @pydantic.field_validator("value")
    def validate_value(cls, value):
        if value is None:
            return False

        value = str(value).lower()

        if value in ["true", "1", "yes", "y", "t"]:
            return True

        return False


class IntervalCatMetadataModel(pydantic.BaseModel):
    value: typing.List[str]
    start_interval_column: str
    end_interval_column: str
    category_column: str
    headers: typing.List[str]
    separator: typing.Optional[str] = pydantic.Field(",")
    default: typing.Optional[str] = None

    def df(self) -> pd.DataFrame:
        rows = [values.split(self.separator) for values in self.value[1:]]
        df = pd.DataFrame(rows, columns=self.headers)

        df[self.start_interval_column] = df[self.start_interval_column].astype(float)
        df[self.end_interval_column] = df[self.end_interval_column].astype(float)

        return df


#######################################################
# Constant Inputs and Outputs
#######################################################


class ConstantInputsModel(pydantic.BaseModel):
    input_void: typing.Optional[InputConnectionModel] = None


class ConstantInputsValueModel(pydantic.BaseModel):
    input_value: InputConnectionModel


class ConstantOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


class ListOutputsModel(pydantic.BaseModel):
    output_list: OutputConnectionModel


class BoolOutputsModel(pydantic.BaseModel):
    output_bool: OutputConnectionModel


#######################################################
# Constant Nodes
#######################################################


class BaseConstant(BaseNode):
    inputs: typing.Optional[ConstantInputsModel] = None

    def kind(self) -> NodeKind:
        return NodeKind.CONSTANT


class Constant(BaseConstant):
    data: ConstantMetadataModel
    outputs: ConstantOutputsModel

    def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        return {"output_value": self.data.value}


class List(BaseConstant):
    data: ListMetadataModel
    outputs: ListOutputsModel

    def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        return {}  # {"output_list": self.data.value}

    def memory_type(self) -> NodeMemoryType:
        return NodeMemoryType.CONSTANT


class Bool(BaseConstant):
    data: BoolMetadataModel = BoolMetadataModel(value=False)
    outputs: BoolOutputsModel

    def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        return {"output_bool": self.data.value}


class IntervalCatV0(BaseConstant):
    data: IntervalCatMetadataModel
    inputs: ConstantInputsValueModel
    outputs: ConstantOutputsModel

    def run(self, input_value: pd.Series) -> typing.Dict[str, typing.Any]:
        values = input_value.astype(float).copy()
        output = pd.Series(np.nan, index=input_value.index, dtype="object")

        for _, row in self.data.df().iterrows():
            output.loc[
                (values >= row[self.data.start_interval_column])
                & (values < float(row[self.data.end_interval_column])),
            ] = row[self.data.category_column]

        if self.data.default is not None:
            output.fillna(self.data.default, inplace=True)

        return {"output_value": output}
