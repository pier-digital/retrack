from retack.engine.nodes.check import CheckNode
from retack.engine.nodes.match import IfNode
from retack.engine.nodes.outputs import BoolOutputNode
from retack.utils.registry import Registry

node_registry = Registry()

node_registry.register("check", CheckNode())
node_registry.register("booloutput", BoolOutputNode())
node_registry.register("if", IfNode())
