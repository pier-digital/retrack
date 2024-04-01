""" Example of rule to get the eighth digit of a CPF."""

import retrack
import pandas as pd

rule = retrack.from_json("examples/cpf-digit.json", validate_version=False)

input_df = pd.DataFrame({"cpf": ["53154432770", "22222224122"]})

print(rule.execute(input_df))
