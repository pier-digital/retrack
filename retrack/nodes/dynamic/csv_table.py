import typing

import pandas as pd
import pydantic

from retrack.nodes.base import InputConnectionModel, OutputConnectionModel
from retrack.nodes.dynamic.base import BaseDynamicNode


class CSVTableMetadataModel(pydantic.BaseModel):
    value: typing.Union[typing.List[str], typing.List[typing.List[str]]]
    target: str
    headers: typing.List[str]
    separator: typing.Optional[str] = ","
    default: typing.Optional[str] = None

    @pydantic.root_validator(pre=True)
    def validate_value(cls, values):
        value, separator = values.get("value", None), values.get("separator", ",")
        if value is None:
            raise ValueError("Value is required")

        for i in range(len(value)):
            value[i] = value[i].split(separator)

        values["value"] = value
        return values


class CSVTableOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


def csv_table_factory(
    inputs: typing.Dict[str, typing.Any], **kwargs
) -> typing.Type[BaseDynamicNode]:
    input_fields = {}

    for name in inputs.keys():
        input_fields[name] = BaseDynamicNode.create_sub_field(InputConnectionModel)

    inputs_model = BaseDynamicNode.with_fields("CSVTableInputsModel", **input_fields)

    models = {
        "inputs": BaseDynamicNode.create_sub_field(inputs_model),
        "outputs": BaseDynamicNode.create_sub_field(CSVTableOutputsModel),
        "data": BaseDynamicNode.create_sub_field(CSVTableMetadataModel),
    }

    BaseCSVTableModel = BaseDynamicNode.with_fields("CSVTable", **models)

    class CSVTableModel(BaseCSVTableModel):
        def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
            input_field_names = list(input_fields.keys())
            csv_df = pd.DataFrame(self.data.value[1:], columns=self.data.value[0])

            response_df = {}

            for name in input_field_names:
                if name not in kwargs.keys():
                    raise ValueError(f"Missing input {name} in CSVTable node")

                response_df[name] = kwargs[name]

            response_df = pd.DataFrame(response_df)
            response_df = response_df.merge(
                csv_df, how="left", left_on=input_field_names
            )

            if self.data.default:
                response_df[self.data.target] = response_df[self.data.target].fillna(
                    self.data.default
                )

            return {"output_value": response_df[self.data.target]}
