<p align="center">
  <a href="https://github.com/pier-digital/retrack"><img src="https://raw.githubusercontent.com/pier-digital/retrack/main/logo.png" alt="retrack"></a>
</p>
<p align="center">
    <em>A business rules engine</em>
</p>

<div align="center">

[![Package version](https://img.shields.io/pypi/v/retrack?color=%2334D058&label=pypi%20package)](https://pypi.org/project/retrack/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/pier-digital/retrack/releases)
[![License](https://img.shields.io/github/license/pier-digital/retrack)](https://github.com/pier-digital/retrack/blob/main/LICENSE)

</div>


## Installation

```bash
pip install retrack
```

## Usage

```python
import retrack

rule = retrack.from_json("rule.json")

result = rule.execute(your_data_df)
```

### Creating a rule/model

A rule is a set of conditions and actions that are executed when the conditions are met. The conditions are evaluated using the data passed to the runner. The actions are executed when the conditions are met.

Each rule is composed of many nodes. To see each node type, check the [nodes](https://github.com/pier-digital/retrack/tree/main/retrack/nodes) folder.

To create a rule, you need to create a JSON file with the following structure:

```json
{
  "nodes": {
		"node id": {
			"id": "node id",
			"data": {},
			"inputs": {},
			"outputs": {},
			"name": "node name",
		},
    // ... more nodes
  }
}
```

The `nodes` key is a dictionary of nodes. Each node has the following properties:

- `id`: The node id. This is used to reference the node in the `inputs` and `outputs` properties.
- `data`: The node data. This is used as a metadata for the node.
- `inputs`: The node inputs. This is used to reference the node inputs.
- `outputs`: The node outputs. This is used to reference the node outputs.
- `name`: The node name. This is used to define the node type.

The `inputs` and `outputs` properties are dictionaries of node connections. Each connection has the following properties:

- `node`: The node id that is connected to the current node.
- `input`: The input name of the connection that is connected to the current node. This is only used in the `inputs` property.
- `output`: The output name of the connection that is connected to the current node. This is only used in the `outputs` property.

To see some examples, check the [examples](https://github.com/pier-digital/retrack/tree/main/examples) folder.

### Creating a custom node

To create a custom node, you need to create a class that inherits from the `BaseNode` class. Each node is a pydantic model, so you can use pydantic features to create your custom node. To see the available features, check the [pydantic documentation](https://pydantic-docs.helpmanual.io/).

To create a custom node you need to define the inputs and outputs of the node. To do this, you need to define the `inputs` and `outputs` class attributes. Let's see an example of a custom node that has two inputs, sum them and return the result:

```python
import retrack
import pydantic
import pandas as pd
import typing


class SumInputsModel(pydantic.BaseModel):
    input_value_0: retrack.InputConnectionModel
    input_value_1: retrack.InputConnectionModel


class SumOutputsModel(pydantic.BaseModel):
    output_value: retrack.OutputConnectionModel


class SumNode(retrack.BaseNode):
    inputs: SumInputsModel
    outputs: SumOutputsModel

    def run(self, input_value_0: pd.Series,
        input_value_1: pd.Series,
    ) -> typing.Dict[str, pd.Series]:
        output_value = input_value_0.astype(float) + input_value_1.astype(float)
        return {
            "output_value": output_value,
        }
```

After creating the custom node, you need to register it in the nodes registry and pass the registry to the parser. Let's see an example:

```python
import retrack

# Register the custom node
custom_registry = retrack.nodes_registry()
custom_registry.register("sum", SumNode)

rule = retrack.from_json("rule.json", nodes_registry=custom_registry)
```

## Contributing

Contributions are welcome! Please read the [contributing guidelines](https://github.com/pier-digital/retrack/tree/main/CONTRIBUTING.md) first.