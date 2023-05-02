import pandas as pd


def to_list(input_list):
    if isinstance(input_list, pd.Series):
        input_list = input_list.to_list()

    return input_list
