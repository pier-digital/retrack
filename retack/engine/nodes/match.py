import typing

import pandas as pd

from retack.engine import constants


class IfNode:
    def __call__(self, input_bool: pd.Series) -> typing.Dict[str, pd.Series]:
        return {
            f"{constants.FILTER_REFERENCE_COLUMN}@output_then_void": input_bool,
            f"{constants.FILTER_REFERENCE_COLUMN}@output_else_void": ~input_bool,
        }
