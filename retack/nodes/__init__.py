from retack.nodes.check import Check
from retack.nodes.constants import Bool, Constant, List
from retack.nodes.inputs import Input
from retack.nodes.match import If
from retack.nodes.outputs import BoolOutput
from retack.nodes.start import Start
from retack.utils.registry import Registry

model_registry = Registry()

model_registry.register("Input", Input)
model_registry.register("Start", Start)
model_registry.register("Constant", Constant)
model_registry.register("List", List)
model_registry.register("Bool", Bool)
model_registry.register("BoolOutput", BoolOutput)
model_registry.register("Check", Check)
model_registry.register("If", If)

__all__ = ["model_registry"]
