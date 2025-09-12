from typing import Optional
import networkx as nx

from retrack.validators.base import BaseValidator


class CheckIsDAG(BaseValidator):
    def validate(self, edges: list, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate the graph data.

        Returns:
            A tuple (is_valid, error_message). is_valid is True if the graph data is valid, False otherwise.
            error_message contains details about the validation failure, or None if validation passed.
        """
        graph = nx.DiGraph()
        graph.add_edges_from(edges)
        result = nx.is_directed_acyclic_graph(graph)
        return result, None if result else "Graph is not a DAG"
