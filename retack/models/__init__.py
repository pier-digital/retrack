from retack.models.constants import ConstantModel, ListModel
from retack.models.inputs import InputModel
from retack.models.start import StartModel
from retack.utils.model_registry import ModelRegistry

model_registry = ModelRegistry()

model_registry.register("Input", InputModel)
model_registry.register("Start", StartModel)
model_registry.register("Constant", ConstantModel)
model_registry.register("List", ListModel)

__all__ = ["model_registry"]
