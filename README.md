<p align="center">
  <a href="https://github.com/gabrielguarisa/retrack"><img src="https://raw.githubusercontent.com/gabrielguarisa/retrack/main/logo.png" alt="retrack"></a>
</p>
<p align="center">
    <em>A business rules engine</em>
</p>

<div align="center">

[![Package version](https://img.shields.io/pypi/v/retrack?color=%2334D058&label=pypi%20package)](https://pypi.org/project/retrack/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/gabrielguarisa/retrack/releases)
[![License](https://img.shields.io/github/license/gabrielguarisa/retrack)](https://github.com/gabrielguarisa/retrack/blob/main/LICENSE)

</div>


## Installation

```bash
pip install retrack
```

## Usage

```python
from retack.engine.parser import Parser
from retack.engine.runner import Runner

# Parse the rule/model
parser = Parser(rule)

# Create a runner
runner = Runner(parser)

# Run the rule/model passing the data
runner(data)
```

### Creating a rule/model

A rule is a set of conditions and actions that are executed when the conditions are met. The conditions are evaluated using the data passed to the runner. The actions are executed when the conditions are met.

Each rule is composed of many nodes. To see each node type, check the [nodes](https://github.com/gabrielguarisa/retrack/tree/main/retrack/nodes) folder.

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

To see some examples, check the [examples](https://github.com/gabrielguarisa/retrack/tree/main/examples) folder.

## Contributing

Contributions are welcome! Please read the [contributing guidelines](https://github.com/gabrielguarisa/retrack/tree/main/CONTRIBUTING.md) first.