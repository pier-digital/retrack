"""Example of using retrack to run a rule/model.
This example uses the age-check.json rule/model to check if a person is older than 18.
"""

import json

import retrack

# Load the rule/model
with open("examples/age-check.json", "r") as f:
    rule = json.load(f)

# Parse the rule/model
parser = retrack.Parser(rule)

# Create a runner
runner = retrack.Runner(parser)

# Run the rule/model passing the data
in_values = [10, -10, 18, 19, 100]
print("Input values:", in_values)
out_values = runner([{"age": val} for val in in_values])
print("Output values:")
print(out_values)
