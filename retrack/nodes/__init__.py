from retrack.nodes.base import BaseNode
from retrack.nodes.check import Check
from retrack.nodes.connectors import BaseConnector, VirtualConnector
from retrack.nodes.constants import Bool, Constant, IntervalCatV0, List
from retrack.nodes.contains import Contains
from retrack.nodes.datetime import CurrentYear
from retrack.nodes.dynamic import BaseDynamicNode
from retrack.nodes.dynamic import registry as dynamic_nodes_registry
from retrack.nodes.endswith import EndsWith
from retrack.nodes.endswithany import EndsWithAny
from retrack.nodes.inputs import Input
from retrack.nodes.logic import And, Not, Or
from retrack.nodes.lowercase import LowerCase
from retrack.nodes.match import If
from retrack.nodes.math import AbsoluteValue, Math, Round
from retrack.nodes.outputs import Output
from retrack.nodes.start import Start
from retrack.nodes.startswith import StartsWith
from retrack.nodes.startswithany import StartsWithAny
from retrack.nodes.substring import IsSubStringOf
from retrack.nodes.getchar import GetChar
from retrack.utils.registry import Registry


def registry() -> Registry:
    """Create a registry with all the nodes available in the library."""
    _registry = Registry()

    _registry.register("Input", Input)
    _registry.register(
        "Connector", VirtualConnector
    )  # By default, Connector is an Input
    _registry.register(
        "ConnectorV0", VirtualConnector
    )  # By default, Connector is an Input
    _registry.register("Start", Start)
    _registry.register("Constant", Constant)
    _registry.register("List", List)
    _registry.register("Bool", Bool)
    _registry.register("Output", Output)
    _registry.register("Check", Check)
    _registry.register("If", If)
    _registry.register("And", And)
    _registry.register("Or", Or)
    _registry.register("Not", Not)
    _registry.register("Math", Math)
    _registry.register("Round", Round)
    _registry.register("AbsoluteValue", AbsoluteValue)
    _registry.register("StartsWith", StartsWith)
    _registry.register("EndsWith", EndsWith)
    _registry.register("StartsWithAny", StartsWithAny)
    _registry.register("EndsWithAny", EndsWithAny)
    _registry.register("Contains", Contains)
    _registry.register("CurrentYear", CurrentYear)
    _registry.register("IntervalCatV0", IntervalCatV0)
    _registry.register("LowerCase", LowerCase)
    _registry.register("IsSubStringOf", IsSubStringOf)
    _registry.register("GetChar", GetChar)

    return _registry


__all__ = [
    "registry",
    "BaseNode",
    "dynamic_nodes_registry",
    "BaseDynamicNode",
    "BaseConnector",
]
