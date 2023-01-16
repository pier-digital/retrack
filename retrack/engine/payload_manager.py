import typing

import pydantic

from retrack.nodes.inputs import Input


class PayloadManager:
    def __init__(self, inputs: typing.List[Input]):
        self._model = None
        self.inputs = inputs

    @property
    def inputs(self) -> typing.List[Input]:
        return self._inputs

    @inputs.setter
    def inputs(self, inputs: typing.List[Input]):
        if not isinstance(inputs, list):
            raise TypeError(f"inputs must be a list, not {type(inputs)}")

        input_names = set()
        formated_inputs = []

        for i in range(len(inputs)):
            if isinstance(inputs[i], dict):
                inputs[i] = Input(**inputs[i])
            elif not isinstance(inputs[i], Input):
                raise TypeError(
                    f"inputs[{i}] must be a dict or an InputModel, not {type(inputs[i])}"
                )

            if inputs[i].data.name not in input_names:
                input_names.add(inputs[i].data.name)
                formated_inputs.append(inputs[i])

        self._inputs = formated_inputs

        if len(self.inputs) > 0:
            self._model = self._create_model()

    @property
    def model(self) -> typing.Type[pydantic.BaseModel]:
        return self._model

    def _create_model(self) -> typing.Type[pydantic.BaseModel]:
        return pydantic.create_model(
            "Payload",
            **{
                input_.data.name: (
                    str,
                    ...,
                )
                for input_ in self.inputs
            },
        )

    def validate(
        self,
        payload: typing.Union[
            typing.Dict[str, str], typing.List[typing.Dict[str, str]]
        ],
    ) -> typing.List[pydantic.BaseModel]:
        if self.model is None:
            raise ValueError("No inputs found")

        if not isinstance(payload, list):
            payload = [payload]

        return pydantic.parse_obj_as(typing.List[self.model], payload)
