import typing

import numpy as np
import pandas as pd

from retack.engine import constants


class BoolOutputNode:
    def __call__(
        self, input_bool: pd.Series, message: str = np.nan
    ) -> typing.Dict[str, pd.Series]:
        return {
            constants.OUTPUT_REFERENCE_COLUMN: input_bool,
            constants.OUTPUT_MESSAGE_REFERENCE_COLUMN: message,
        }
