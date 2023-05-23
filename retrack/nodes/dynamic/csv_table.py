import typing

import pandas as pd
import pydantic

from retrack.nodes.base import InputConnectionModel, OutputConnectionModel
from retrack.nodes.dynamic.base import BaseDynamicIOModel, BaseDynamicNode


class CSVTableMetadataModel(pydantic.BaseModel):
    value: typing.Union[typing.List[str], typing.List[typing.List[str]]]
    target: str
    headers: typing.List[str]
    headers_map: typing.List[str]
    separator: typing.Optional[str] = ","
    default: typing.Optional[str] = None
    
    def df(self) -> pd.DataFrame:
        rows = [values.split(self.separator) for values in self.value[1:]]
        return pd.DataFrame(rows, columns=self.headers_map)


class CSVTableOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


def csv_table_factory(
    inputs: typing.Dict[str, typing.Any], **kwargs
) -> typing.Type[BaseDynamicNode]:
    input_fields = {}

    for name in inputs.keys():
        input_fields[name] = BaseDynamicNode.create_sub_field(InputConnectionModel)

    inputs_model = BaseDynamicIOModel.with_fields("CSVTableInputsModel", **input_fields)

    models = {
        "inputs": BaseDynamicNode.create_sub_field(inputs_model),
        "outputs": BaseDynamicNode.create_sub_field(CSVTableOutputsModel),
        "data": BaseDynamicNode.create_sub_field(CSVTableMetadataModel),
    }

    BaseCSVTableModel = BaseDynamicNode.with_fields("CSVTable", **models)

    class CSVTableModel(BaseCSVTableModel):
        def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
            csv_df = self.data.df()

            response_df = {}

            input_columns = [
                name for name in self.data.headers_map if name != self.data.target
            ]

            for name in input_columns:
                if name == self.data.target:
                    continue

                if name not in kwargs.keys():
                    raise ValueError(f"Missing input {name} in CSVTable node")

                response_df[name] = kwargs[name]

            response_df = pd.DataFrame(response_df)
            response_df = response_df.astype(str)
            response_df = response_df.merge(csv_df, how="left", on=input_columns)

            if self.data.default:
                response_df[self.data.target] = response_df[self.data.target].fillna(
                    self.data.default
                )

            return {"output_value": response_df[self.data.target]}

    return CSVTableModel
