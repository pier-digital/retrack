import typing

import pandas as pd
import pydantic

from retrack.nodes.base import InputConnectionModel, OutputConnectionModel
from retrack.nodes.dynamic.base import BaseDynamicIOModel, BaseDynamicNode


class CSVTableV0MetadataModel(pydantic.BaseModel):
    value: typing.Union[typing.List[str], typing.List[typing.List[str]]]
    target: str
    headers: typing.List[str]
    headers_map: typing.List[str]
    separator: typing.Optional[str] = ","
    default: typing.Optional[str] = None

    def df(self) -> pd.DataFrame:
        rows = [values.split(self.separator) for values in self.value[1:]]
        return pd.DataFrame(rows, columns=self.headers_map)


class CSVTableV0OutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


def csv_table_factory(
    inputs: typing.Dict[str, typing.Any], **kwargs
) -> typing.Type[BaseDynamicNode]:
    input_fields = {}

    for name in inputs.keys():
        input_fields[name] = BaseDynamicNode.create_sub_field(InputConnectionModel)

    inputs_model = BaseDynamicIOModel.with_fields(
        "CSVTableV0InputsModel", **input_fields
    )

    models = {
        "inputs": BaseDynamicNode.create_sub_field(inputs_model),
        "outputs": BaseDynamicNode.create_sub_field(CSVTableV0OutputsModel),
        "data": BaseDynamicNode.create_sub_field(CSVTableV0MetadataModel),
    }

    BaseCSVTableV0Model = BaseDynamicNode.with_fields("CSVTableV0", **models)

    class CSVTableV0(BaseCSVTableV0Model):
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
                    raise ValueError(f"Missing input {name} in CSVTableV0 node")

                response_df[name] = kwargs[name]

            response_df = pd.DataFrame(response_df)
            response_df = response_df.astype(str)
            response_df = response_df.merge(csv_df, how="left", on=input_columns)

            if self.data.default:
                response_df[self.data.target] = response_df[self.data.target].fillna(
                    self.data.default
                )

            response_df.set_index(
                kwargs[input_columns[0]].index, inplace=True, drop=True
            )

            return {"output_value": response_df[self.data.target]}

    return CSVTableV0
