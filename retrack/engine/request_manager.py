import typing

import pandas as pd
import pandera
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
        return [input.data.name for input in self.inputs]

    @inputs.setter
    def inputs(self, inputs: typing.List[BaseNode]):
        if not isinstance(inputs, list):
            raise TypeError(f"inputs must be a list, not {type(inputs)}")

        input_names = set()
        formated_inputs = []

        for i in range(len(inputs)):
            if not isinstance(inputs[i], BaseNode):
                raise TypeError(
                    f"inputs[{i}] must be a dict or an InputModel, not {type(inputs[i])}"
                )

            if inputs[i].kind() != NodeKind.INPUT:
                raise TypeError(
                    f"inputs[{i}] must be an InputModel, not {type(inputs[i])}"
                )

            if inputs[i].data.name not in input_names:
                input_names.add(inputs[i].data.name)
                formated_inputs.append(inputs[i])

        self._inputs = formated_inputs

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
    def dataframe_model(self) -> pandera.DataFrameSchema:
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
        for input_field in self.inputs:
            fields[input_field.data.name] = (
                typing.Annotated[
                    str if input_field.data.default is None else typing.Optional[str],
                    pydantic.BeforeValidator(
                        StrFieldValidator(input_field.data.default)
                    ),
                ],
                pydantic.Field(
                    default=Ellipsis
                    if input_field.data.default is None
                    else input_field.data.default,
                    optional=input_field.data.default is not None,
                    validate_default=False,
                ),
            )

        return pydantic.create_model(
            model_name,
            **fields,
        )

    def __create_dataframe_model(self) -> pandera.DataFrameSchema:
        """Create a pydantic model from the RequestManager's inputs"""
        fields = {}
        for input_field in self.inputs:
            fields[input_field.data.name] = pandera.Column(
                str,
                nullable=input_field.data.default is not None,
                coerce=True,
                default=input_field.data.default,
            )

        return pandera.DataFrameSchema(
            fields,
            index=pandera.Index(int),
            # strict=True,
            coerce=True,
        )

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

        return self.dataframe_model.validate(payload)
