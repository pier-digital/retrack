import pandas as pd
import typing

class BoolOutputNode:
    def __call__(self, input_bool: pd.Series) -> typing.Dict[str, pd.Series]:
        return {"OUTPUT": input_bool}