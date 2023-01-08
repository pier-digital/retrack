import typing

import pydantic

###############################################################
# Connection Models
###############################################################


class OutputConnectionItemModel(pydantic.BaseModel):
    node: str
    input_: str = pydantic.Field(alias="input")


class InputConnectionItemModel(pydantic.BaseModel):
    node: str
    output: str = pydantic.Field(alias="output")


class OutputConnectionModel(pydantic.BaseModel):
    connections: typing.List[OutputConnectionItemModel]


class InputConnectionModel(pydantic.BaseModel):
    connections: typing.List[InputConnectionItemModel]


###############################################################
# Base Node
###############################################################


class BaseNode(pydantic.BaseModel):
    id: str
    inputs: typing.Optional[typing.Dict[str, InputConnectionModel]] = None
    outputs: typing.Optional[typing.Dict[str, OutputConnectionModel]] = None

    def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
        raise {}

    @property
    def node_name(self):
        return self.__class__.__name__

    @property
    def output_names(self) -> typing.List[str]:
        if not hasattr(self, "outputs") or self.outputs is None:
            return []
        return list(self.outputs.dict(by_alias=True).keys())

    @property
    def input_names(self) -> typing.List[str]:
        if not hasattr(self, "inputs") or self.inputs is None:
            return []
        return list(self.inputs.dict(by_alias=True).keys())

    def get_output_connections(
        self, output_name: str
    ) -> typing.List[OutputConnectionItemModel]:
        if self.outputs is None:
            return []
        if output_name not in self.outputs:
            return []
        return self.outputs[output_name].connections

    def get_input_connections(
        self, input_name: str
    ) -> typing.List[InputConnectionItemModel]:
        if self.inputs is None:
            return []
        if input_name not in self.inputs:
            return []
        return self.inputs[input_name].connections

    def get_output_connection_ids(self, output_name: str = None) -> typing.List[str]:
        if output_name is not None:
            return [c.node for c in self.get_output_connections(output_name)]

        output_name = self.output_names
        output = []
        for output_name in output_name:
            output.extend(self.get_output_connection_ids(output_name))
        return output

    def get_input_connection_ids(self, input_name: str = None) -> typing.List[str]:
        if input_name is not None:
            return [c.node for c in self.get_input_connections(input_name)]

        input_names = self.input_names
        input = []
        for input_name in input_names:
            input.extend(self.get_input_connection_ids(input_name))
        return input
