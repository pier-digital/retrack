from typing import Optional

from retrack.validators.base import BaseValidator


class SingleTerminalNodeValidator(BaseValidator):
    """Prevents mixing Output and MultipleOutputs nodes in the same graph.

    Multiple Output nodes are valid (used in conditional branches). Multiple
    MultipleOutputs nodes are also valid. What is not valid is having both
    types simultaneously, because their output contracts are incompatible.
    """

    def validate(self, graph_data: dict, **kwargs) -> tuple[bool, Optional[str]]:
        nodes = graph_data.get("nodes", {})

        has_output = any(
            node.get("name", "").lower() == "output"
            for _, node in nodes.items()
        )
        has_multiple_outputs = any(
            node.get("name", "").lower() == "multipleoutputs"
            for _, node in nodes.items()
        )

        if has_output and has_multiple_outputs:
            return (
                False,
                "Graph cannot mix Output and MultipleOutputs nodes in the same flow",
            )
        return True, None
