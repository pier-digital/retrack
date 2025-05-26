import json
import typing

import pandas as pd
import numpy as np
import pydantic

from retrack.nodes.base import InputConnectionModel, OutputConnectionModel
from retrack.nodes.dynamic.base import BaseDynamicIOModel, BaseDynamicNode


LINK_FUNCS = {
    "identity": lambda eta: eta,
    "log": np.log,
    "exponential": np.exp,
    "logit": lambda eta: np.log(eta / (1 - eta)),
    "inverse": lambda eta: 1.0 / eta,
}


class GLMMetadataModel(pydantic.BaseModel):
    value: str
    name: typing.Optional[str] = None
    default: typing.Optional[str] = None
    link: typing.Optional[str] = "log"
    headers_map: typing.Dict[str, int]

    def parsed_value(self) -> typing.Dict[str, typing.Any]:
        return json.loads(self.value)

    def intercept(self) -> float:
        parsed = self.parsed_value()
        return float(parsed.get("intercept", 0.0))


class GLMOutputsModel(pydantic.BaseModel):
    output_value: OutputConnectionModel


def glm_factory(
    inputs: typing.Dict[str, typing.Any],
    **factory_kwargs,
) -> typing.Type[BaseDynamicNode]:
    input_fields = {}

    for name in inputs.keys():
        input_fields[name] = BaseDynamicNode.create_sub_field(InputConnectionModel)

    inputs_model = BaseDynamicIOModel.with_fields("GLMInputsModel", **input_fields)

    models = {
        "inputs": BaseDynamicNode.create_sub_field(inputs_model),
        "outputs": BaseDynamicNode.create_sub_field(GLMOutputsModel),
        "data": BaseDynamicNode.create_sub_field(GLMMetadataModel),
    }

    BaseGLMModel = BaseDynamicNode.with_fields("GLM", **models)

    class GLM(BaseGLMModel):
        def run(self, **kwargs) -> typing.Dict[str, typing.Any]:
            weights = self.data.parsed_value()

            intercept = self.data.intercept()

            _example_input: pd.Series = kwargs.get("input_value_0")
            dot = pd.Series(
                np.zeros(len(_example_input)), dtype=float, index=_example_input.index
            )

            for feature_name, index in self.data.headers_map.items():
                field_name = f"input_value_{index}"
                if field_name not in kwargs:
                    raise ValueError(f"Missing input {field_name} in GLM node")

                if feature_name not in weights:
                    raise ValueError(
                        f"Missing weight for feature {feature_name} in GLM node"
                    )

                dot += kwargs[field_name].astype(float) * float(weights[feature_name])

            response = LINK_FUNCS[self.data.link](intercept + dot.astype(float))

            return {"output_value": response}

    return GLM
