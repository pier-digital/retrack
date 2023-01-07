import typing

import numpy as np
import pandas as pd

from retack.engine.nodes import node_registry
from retack.engine.payload_manager import PayloadManager
from retack.parser import Parser
from retack.utils import graph


class Runner:
    def __init__(self, parser: Parser):
        self._parser = parser

        input_elements = self._parser.get_elements_by_kind("input")
        self._input_new_columns = {
            element.data.name: f"{element.id}@output_value"
            for element in input_elements
        }
        self._payload_manager = PayloadManager(input_elements)

        constant_elements = self._parser.get_elements_by_kind("constant")
        self._constants = {
            f"{element.id}@output_value": element.data.value
            for element in constant_elements
        }

        # self._execution_order = graph.get_execution_order(self._parser)
        self._state_df = None

        start_elements = self._parser.get_elements_by_name("start")
        if len(start_elements) == 0:
            raise ValueError("No start element found")
        elif len(start_elements) > 1:
            raise ValueError("Multiple start elements found")

        self._start_element_id = start_elements[0].id
        self._filters = {}

    def _payload_to_dataframe(self, payload: typing.Union[dict, list]) -> pd.DataFrame:
        validated_payload = self.payload_manager.validate(payload)
        validated_payload = [p.dict() for p in validated_payload]

        return pd.DataFrame(validated_payload)

    @property
    def payload_manager(self) -> PayloadManager:
        return self._payload_manager

    def run_element(self, element_id: str):
        element = self._parser.get_element_by_id(element_id).dict(by_alias=True)
        element_name = self._parser.get_name_by_id(element_id)
        # print(element_id, self._parser.get_name_by_id(element_id))
        input_params = element.get("data", {})

        for connector_name, connections in element.get("inputs", {}).items():
            if connector_name.endswith("void"):
                continue

            for connection in connections["connections"]:
                input_params[connector_name] = self._state_df.loc[
                    self._filters.get(element_id, None) :,
                    f"{connection['node']}@{connection['output']}",
                ]

        node_executor = node_registry.get(element_name)

        # print(element_id, input_params)
        if node_executor:
            output = node_executor(**input_params)
            for output_name, output_value in output.items():
                if output_name == "OUTPUT":
                    self._state_df.loc[self._filters.get(element_id, None):, "OUTPUT"] = output_value
                elif output_name == "FILTER":
                    output_connections = graph.get_element_connections(
                        element, is_input=False
                    )
                    for output_connection in output_connections:
                        if self._filters.get(output_connection, None) is None:
                            self._filters[output_connection] = output_value
                        else:
                            self._filters[output_connection] = (
                                self._filters[output_connection] & output_value
                            )
                else:
                    self._state_df.loc[self._filters.get(element_id, None):, f"{element_id}@{output_name}"] = output_value

    def __call__(self, payload: typing.Union[dict, list]):
        self._state_df = self._payload_to_dataframe(payload)
        self._state_df = self._state_df.rename(columns=self._input_new_columns)

        for constant_name, constant_value in self._constants.items():
            self._state_df[constant_name] = constant_value

        self._state_df["OUTPUT"] = np.nan

        graph.walk(self._parser, self._start_element_id, callback=self.run_element)

        return self._state_df["OUTPUT"].to_list()
