import typing

import pandas as pd

from retrack.nodes.base import BaseNode, NodeKind


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

            if inputs[i].data.name not in formated_inputs:
                formated_inputs[inputs[i].data.name] = inputs[i]
            elif inputs[i].data.default is not None:
                formated_inputs[inputs[i].data.name] = inputs[i]

        self._inputs = formated_inputs.values()

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
        if not isinstance(payload, pd.DataFrame):
            raise TypeError(f"payload must be a pandas.DataFrame, not {type(payload)}")

        for input_node in self.inputs:
            if input_node.data.name not in payload.columns:
                if input_node.data.default is not None:
                    payload[input_node.data.name] = input_node.data.default
                else:
                    raise ValueError(f"Missing required input: {input_node.data.name}")

        payload.replace(
            {pd.NA: None, "None": None, "": None, "null": None}, inplace=True
        )

        return payload
