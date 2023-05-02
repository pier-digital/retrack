from retrack.nodes.base import BaseNode
from retrack.nodes.check import Check
from retrack.nodes.constants import Bool, Constant, List
from retrack.nodes.contains import Contains
from retrack.nodes.endswith import EndsWith
from retrack.nodes.endswithany import EndsWithAny
from retrack.nodes.inputs import Input
from retrack.nodes.logic import And, Not, Or
from retrack.nodes.match import If
from retrack.nodes.math import Math
from retrack.nodes.outputs import Output
from retrack.nodes.start import Start
from retrack.nodes.startswith import StartsWith
from retrack.nodes.startswithany import StartsWithAny
from retrack.utils.registry import Registry

_registry = Registry()


def registry() -> Registry:
    return _registry


def register(name: str, node: BaseNode) -> None:
    registry().register(name, node)


register("Input", Input)
register("Start", Start)
register("Constant", Constant)
register("List", List)
register("Bool", Bool)
register("Output", Output)
register("Check", Check)
register("If", If)
register("And", And)
register("Or", Or)
register("Not", Not)
register("Math", Math)
register("StartsWith", StartsWith)
register("EndsWith", EndsWith)
register("StartsWithAny", StartsWithAny)
register("EndsWithAny", EndsWithAny)
register("Contains", Contains)

__all__ = ["registry", "register", "BaseNode"]
