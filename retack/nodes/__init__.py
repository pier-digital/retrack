from retack.nodes.base import BaseNode
from retack.nodes.check import Check
from retack.nodes.constants import Bool, Constant, List
from retack.nodes.contains import Contains
from retack.nodes.endswith import EndsWith
from retack.nodes.endswithany import EndsWithAny
from retack.nodes.inputs import Input
from retack.nodes.logic import And, Not, Or
from retack.nodes.match import If
from retack.nodes.math import Math
from retack.nodes.outputs import BoolOutput
from retack.nodes.start import Start
from retack.nodes.startswith import StartsWith
from retack.nodes.startswithany import StartsWithAny
from retack.utils.registry import Registry

registry = Registry()

registry.register("Input", Input)
registry.register("Start", Start)
registry.register("Constant", Constant)
registry.register("List", List)
registry.register("Bool", Bool)
registry.register("BoolOutput", BoolOutput)
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
