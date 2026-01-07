import typing

import pandas as pd


def to_list(input_list):
    if isinstance(input_list, pd.Series):
        input_list = input_list.to_list()

    return input_list


def to_normalized_dict(df: pd.DataFrame, key_name: str = "name") -> typing.List[dict]:
    """Convert DataFrame columns to list of dicts with name and values."""
    return [
        {key_name: k, "values": list(v.values())}
        for k, v in df.to_dict(orient="dict").items()
    ]
