"""
A Collection of interfaces describing how data is used in the system.
Here, 'Data' means something analogous to ADTs
"""
import abc
from dataclasses import dataclass, field
from typing import Any, Dict
from acab.abstract.interfaces.handler_system_interface import HandlerComponent

Value              = 'AcabValue'
Node               = 'NodeInterface'
DependentSemantics = 'DependentSemantics'

@dataclass
class NodeInterface(metaclass=abc.ABCMeta):
    """  """

    value : Value
    children : Dict[str, Node] = field(init=False, default_factory=dict)

    @staticmethod
    @abc.abstractmethod
    def Root() -> Node:
        """ Construct a root node for a data structure """
        pass


    @abc.abstractmethod
    def _default_setup(self, path: [Node], data: Dict[Any,Any], context: Dict[Any,Any]):
        """ Called by a Semantics upon creation of a new node """
        pass

    @abc.abstractmethod
    def _update_node(self, path, data, context):
        """ Called by a semantics for passing through a node """
        pass

    @abc.abstractmethod
    def add_child(self, node) -> Node:
        pass

    @abc.abstractmethod
    def get_child(self, node) -> Node:
        pass

    @abc.abstractmethod
    def has_child(self, node) -> bool:
        pass

    @abc.abstractmethod
    def remove_child(self, node) -> Node:
        pass

    @abc.abstractmethod
    def clear_children(self):
        pass


@dataclass
class StructureInterface(HandlerComponent):
    """ The structures which semantics operate on """
    root       : Node           = field()
    components : Dict[str, Any] = field(init=False, default_factory=dict)

    @staticmethod
    @abc.abstractmethod
    def build_default() -> 'Structure':
        pass

    @abc.abstractmethod
    def __bool__(self) -> bool:
        """ Is the Structure Empty? """
        pass
