import typing

import pandas as pd


class BoolOutputNode:
    def __call__(self, input_bool: pd.Series) -> typing.Dict[str, pd.Series]:
        return {"OUTPUT": input_bool}
