import typing

import pandas as pd

from retack.engine import constants


class BoolOutputNode:
    def __call__(self, input_bool: pd.Series) -> typing.Dict[str, pd.Series]:
        return {constants.OUTPUT_REFERENCE_COLUMN: input_bool}
