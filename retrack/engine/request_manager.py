import typing

import pydantic

from retrack.nodes.base import BaseNode, NodeKind


class RequestManager:
    def __init__(self, inputs: typing.List[BaseNode]):
        self._model = None
        self.inputs = inputs

    @property
    def inputs(self) -> typing.List[BaseNode]:
        return self._inputs

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
        else:
            self._model = None

    @property
    def model(self) -> typing.Type[pydantic.BaseModel]:
        return self._model

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
                (str, ...)
                if input_field.data.default is None
                else (str, input_field.data.default)
            )

        return pydantic.create_model(
            model_name,
            **fields,
        )

    def validate(
        self,
        payload: typing.Union[
            typing.Dict[str, str], typing.List[typing.Dict[str, str]]
        ],
    ) -> typing.List[pydantic.BaseModel]:
        """Validate the payload against the RequestManager's model

        Args:
            payload (typing.Union[typing.Dict[str, str], typing.List[typing.Dict[str, str]]]): The payload to validate

        Raises:
            ValueError: If the RequestManager has no model

        Returns:
            typing.List[pydantic.BaseModel]: The validated payload
        """
        if self.model is None:
            raise ValueError("No inputs found")

        if not isinstance(payload, list):
            payload = [payload]

        return pydantic.parse_obj_as(typing.List[self.model], payload)
