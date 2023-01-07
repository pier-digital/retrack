from retack.models.check import CheckModel
from retack.models.constants import BoolModel, ConstantModel, ListModel
from retack.models.inputs import InputModel
from retack.models.match import IfModel
from retack.models.outputs import BoolOutputModel
from retack.models.start import StartModel
from retack.utils.registry import Registry

model_registry = Registry()

model_registry.register("Input", InputModel)
model_registry.register("Start", StartModel)
model_registry.register("Constant", ConstantModel)
model_registry.register("List", ListModel)
model_registry.register("Bool", BoolModel)
model_registry.register("BoolOutput", BoolOutputModel)
model_registry.register("Check", CheckModel)
model_registry.register("If", IfModel)

__all__ = ["model_registry"]
