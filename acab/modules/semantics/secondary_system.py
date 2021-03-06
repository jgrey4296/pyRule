# Main System
import logging as root_logger
from dataclasses import InitVar, dataclass, field
from typing import (Any, Callable, ClassVar, Dict, Generic, Iterable, Iterator,
                    List, Mapping, Match, MutableMapping, Optional, Sequence,
                    Set, Tuple, TypeVar, Union, cast)

from acab.abstract.config.config import AcabConfig
from acab.abstract.interfaces.semantic_interfaces import (AbstractionSemantics,
                                                          SemanticSystem)
from acab.error.acab_semantic_exception import AcabSemanticException
from acab.modules.semantics.context_container import ContextContainer


logging = root_logger.getLogger(__name__)

Sentence = 'Sentence'
CtxCon   = 'ContextContainer'

config  = AcabConfig.Get()

SEM_HINT = config.prepare("Value.Structure", "SEMANTIC_HINT")()

@dataclass
class GuaranteeSemanticSystem(SemanticSystem):
    """  """
    # Downward guarantees of what semantics may contextually rely upon
    guarantees        : Set['Handler']               = field(default_factory=list)
    # Downward expectations of what semantics must publicly provide
    expectations      : Set['SemanticUnion']         = field(init=False, default_factory=list)

    def __init__(self):
        raise NotImplementedError()
