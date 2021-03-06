"""
A Collection of interfaces describing how information in context is collected, constrained,
and grouped for communication between system components
"""

from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

import abc
from dataclasses import dataclass, field, InitVar

# Type declarations:

# Interfaces:
@dataclass
class ConstraintInterface(metaclass=abc.ABCMeta):
    @staticmethod
    def build(word, operators):
        pass

    @abc.abstractmethod
    def test_all(self, node, ctx):
        pass

@dataclass
class ContextContainer(metaclass=abc.ABCMeta):

    @staticmethod
    def build(ops):
        pass

    @abc.abstractmethod
    def __call__(self, root_node, query_sen, data, collapse_vars, is_negated):
        pass

    @abc.abstractmethod
    def __enter__(self):
        pass

    @abc.abstractmethod
    def __exit__(self):
        pass

    @abc.abstractmethod
    def fail(self, instance, word, node):
        pass

    @abc.abstractmethod
    def test(self, ctx, possible, word):
        pass

    @abc.abstractmethod
    def push(self, ctxs):
        pass

    @abc.abstractmethod
    def pop(self, top=False):
        pass

@dataclass
class ContextInstance(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def bind(self, word, nodes):
        pass

    @abc.abstractmethod
    def bind_dict(self, the_dict):
        pass

    @abc.abstractmethod
    def __contains__(self, value):
        pass

    @abc.abstractmethod
    def __getitem__(self, value):
        pass
