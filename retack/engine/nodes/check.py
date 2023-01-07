import typing

import pandas as pd

from retack.models.check import CheckOperator


class CheckNode:
    def __call__(
        self,
        input_value_0: pd.Series,
        input_value_1: pd.Series,
        operator: CheckOperator,
    ) -> typing.Dict[str, pd.Series]:
        if operator == CheckOperator.EQUAL:
            return {"output_bool": input_value_0 == input_value_1}
        elif operator == CheckOperator.NOT_EQUAL:
            return {"output_bool": input_value_0 != input_value_1}
        elif operator == CheckOperator.GREATER_THAN:
            return {
                "output_bool": input_value_0.astype(float) > input_value_1.astype(float)
            }
        elif operator == CheckOperator.LESS_THAN:
            return {
                "output_bool": input_value_0.astype(float) < input_value_1.astype(float)
            }
        elif operator == CheckOperator.GREATER_THAN_OR_EQUAL:
            return {
                "output_bool": input_value_0.astype(float)
                >= input_value_1.astype(float)
            }
        elif operator == CheckOperator.LESS_THAN_OR_EQUAL:
            return {
                "output_bool": input_value_0.astype(float)
                <= input_value_1.astype(float)
            }
        else:
            raise ValueError("Unknown operator")
