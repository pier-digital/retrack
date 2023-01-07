import typing

import pandas as pd

from retack.engine.payload_manager import PayloadManager
from retack.parser import Parser
from retack.utils.graph import get_execution_order



class Runner:
    def __init__(self, parser: Parser):
        self._parser = parser

        input_elements = self._parser.get_elements_by_kind("input")
        self._input_new_columns = {element.data.name: f"{element.id}@output_value" for element in input_elements}
        self._payload_manager = PayloadManager(
            input_elements
        )

        constant_elements = self._parser.get_elements_by_kind("constant")
        self._constants = {f"{element.id}@output_value": element.data.value for element in constant_elements}

        self._execution_order = get_execution_order(self._parser)


    def _payload_to_dataframe(self, payload: typing.Union[dict, list]) -> pd.DataFrame:
        validated_payload = self.payload_manager.validate(payload)
        validated_payload = [p.dict() for p in validated_payload]

        return pd.DataFrame(validated_payload)

    @property
    def payload_manager(self) -> PayloadManager:
        return self._payload_manager

    def __call__(self, payload: typing.Union[dict, list]):
        state_df = self._payload_to_dataframe(payload)
        state_df = state_df.rename(columns=self._input_new_columns)

        for constant_name, constant_value in self._constants.items():
            state_df[constant_name] = constant_value

        state_df["OUTPUT"] = None

        for element_id in self._execution_order:
            element = self._parser.get_element_by_id(element_id).dict(by_alias=True)
            input_params = {}
            # print(element_id)
            # print("inputs", element.get("inputs", {}))
            for connector_name, connections in element.get("inputs", {}).items():
                if connector_name.endswith("void"):
                    continue

                for connection in connections["connections"]:
                    input_params[connector_name] = state_df[f"{connection['node']}@{connection['output']}"]

            print(element_id, input_params)
            # TODO run element



            # print("outputs", element.get("outputs", {}))
        #     element = self._parser.get_element_by_id(element_id)
        #     element_name = self._parser.get_name_by_id(element_id)

        #     input_ids = self._parser.get_element_connections(element, is_input=True)
        #     input_data = state_df[input_ids].to_dict(orient="records")

        #     output_ids = self._parser.get_element_connections(element, is_input=False)
        #     output_data = state_df[output_ids].to_dict(orient="records")

        #     output = element.run(input_data, output_data)
        #     state_df.loc[:, element_id] = output
        
        return state_df
