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

registry = Registry()

registry.register("Input", Input)
registry.register("Start", Start)
registry.register("Constant", Constant)
registry.register("List", List)
registry.register("Bool", Bool)
registry.register("Output", Output)
registry.register("Check", Check)
registry.register("If", If)
registry.register("And", And)
registry.register("Or", Or)
registry.register("Not", Not)
registry.register("Math", Math)
registry.register("StartsWith", StartsWith)
registry.register("EndsWith", EndsWith)
registry.register("StartsWithAny", StartsWithAny)
registry.register("EndsWithAny", EndsWithAny)
registry.register("Contains", Contains)

__all__ = ["registry", "BaseNode"]
