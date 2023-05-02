import networkx as nx

from retrack.validators.base import BaseValidator


class CheckIsDAG(BaseValidator):
    def validate(self, edges: list, **kwargs) -> bool:
        """Validate the graph data.

        Returns:
            True if the graph data is valid, False otherwise.
        """
        graph = nx.DiGraph()
        graph.add_edges_from(edges)
        return nx.is_directed_acyclic_graph(graph)
