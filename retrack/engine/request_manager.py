import typing

import pandas as pd
import pydantic

from retrack.nodes.base import BaseNode, NodeKind


class StrFieldValidator:
    def __init__(self, default: typing.Optional[typing.Any] = None):
        self.default = default

    def __call__(self, value: typing.Any) -> typing.Any:
        if value in [None, "None", "", "null"]:
            if self.default is None:
                raise ValueError("value cannot be None")
            else:
                return self.default

        return str(value) if not isinstance(value, str) else value


class RequestManager:
    def __init__(self, inputs: typing.List[BaseNode]):
        self._model = None
        self._dataframe_model = None
        self.inputs = inputs

    @property
    def inputs(self) -> typing.List[BaseNode]:
        return self._inputs

    @property
    def input_names(self) -> typing.List[str]:
        return list(self._columns.keys())

    @inputs.setter
    def inputs(self, inputs: typing.List[BaseNode]):
        if not isinstance(inputs, list):
            raise TypeError(f"inputs must be a list, not {type(inputs)}")

        formated_inputs = {}

        for i in range(len(inputs)):
            if not isinstance(inputs[i], BaseNode):
                raise TypeError(
                    f"inputs[{i}] must be an InputModel, not {type(inputs[i])}"
                )

            if (
                inputs[i].kind() != NodeKind.INPUT
                and inputs[i].kind() != NodeKind.CONNECTOR
            ):
                raise TypeError(
                    f"inputs[{i}] must be an InputModel, not {type(inputs[i])}"
                )

            for column in inputs[i].payload_columns().values():
                if column not in formated_inputs:
                    formated_inputs[column] = inputs[i]
                elif inputs[i].data.default is not None:
                    formated_inputs[column] = inputs[i]

        self._columns = {
            column: node.data.default for column, node in formated_inputs.items()
        }
        self._inputs = list(
            {id(node): node for node in formated_inputs.values()}.values()
        )

        if len(self.inputs) > 0:
            self._model = self.__create_model()
            self._dataframe_model = self.__create_dataframe_model()
        else:
            self._model = None
            self._dataframe_model = None

    @property
    def model(self) -> typing.Type[pydantic.BaseModel]:
        return self._model

    @property
    def dataframe_model(self):
        return self._dataframe_model

    def __create_model(
        self, model_name: str = "RequestModel"
    ) -> typing.Type[pydantic.BaseModel]:
        """Create a pydantic model from the RequestManager's inputs

        Args:
            model_name (str, optional): The name of the model. Defaults to "RequestModel".

        Returns:
            typing.Type[pydantic.BaseModel]: The pydantic model
        """
        fields = {}
        for column, default in self._columns.items():
            fields[column] = (
                typing.Annotated[
                    str if default is None else typing.Optional[str],
                    pydantic.BeforeValidator(StrFieldValidator(default)),
                ],
                pydantic.Field(
                    default=Ellipsis if default is None else default,
                    json_schema_extra={"optional": default is not None},
                    validate_default=False,
                ),
            )

        return pydantic.create_model(
            model_name,
            **fields,
            __config__=pydantic.ConfigDict(
                from_attributes=True, use_enum_values=True, protected_namespaces={}
            ),
        )

    def __create_dataframe_model(self) -> dict:
        """Create a lightweight validation schema from the RequestManager's inputs.

        Returns:
            dict: mapping column_name -> {"nullable": bool, "default": value}
        """
        schema = {}
        for column, default in self._columns.items():
            schema[column] = {
                "nullable": default is not None,
                "default": default,
            }
        return schema

    def validate(
        self,
        payload: pd.DataFrame,
    ) -> pd.DataFrame:
        """Validate the payload against the RequestManager's model

        Args:
            payload (pandas.DataFrame): The payload to validate

        Raises:
            ValueError: If the RequestManager has no model

        Returns:
            pd.DataFrame: The validated payload
        """
        if self.model is None:
            raise ValueError("No inputs found")

        if not isinstance(payload, pd.DataFrame):
            raise TypeError(f"payload must be a pandas.DataFrame, not {type(payload)}")

        schema = self.dataframe_model

        # Check required columns exist
        missing = set(schema.keys()) - set(payload.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        result = payload.copy()

        for col_name, col_schema in schema.items():
            series = result[col_name]

            # Handle nulls
            null_mask = series.isna() | series.isin([None, "None", "", "null"])
            if null_mask.any():
                if not col_schema["nullable"]:
                    raise ValueError(
                        f"Column '{col_name}' contains null values but is not nullable"
                    )
                if col_schema["default"] is not None:
                    series = series.where(~null_mask, col_schema["default"])

            # Coerce to str
            result[col_name] = series.astype(str)

        return result
