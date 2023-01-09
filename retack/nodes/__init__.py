from retack.nodes.base import BaseNode
from retack.nodes.check import Check
from retack.nodes.constants import Bool, Constant, List
from retack.nodes.inputs import Input
from retack.nodes.logic import And
from retack.nodes.match import If
from retack.nodes.outputs import BoolOutput
from retack.nodes.start import Start
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

__all__ = ["registry", "BaseNode"]
