"""
A Trie Structure, using AcabNodes
"""
import logging as root_logger
from weakref import WeakValueDictionary, ref, proxy
from re import search

from acab.abstract.core.sentence import Sentence
from acab.abstract.core.value import AcabValue, AcabStatement
from acab.abstract.data.node import AcabNode
from acab.abstract.data.contexts import Contexts, CTX_OP
from acab.abstract.data.structure import DataStructure
from acab.abstract.rule.query import QueryComponent

from acab.error.acab_base_exception import AcabBaseException
from acab.modules.semantics.basic_semantics import BasicNodeSemantics

from .trie_semantics import BasicTrieSemantics

from acab.config import AcabConfig
util = AcabConfig.Get()

CONSTRAINT_S = util("Parsing.Structure", "CONSTRAINT_S")
AT_BIND_S = util("Parsing.Structure", "AT_BIND_S")

logging = root_logger.getLogger(__name__)

class Trie(DataStructure):

    def __init__(self, semantics=None):
        if semantics is None:
            semantics = BasicTrieSemantics({AcabNode : BasicNodeSemantics()},
                                           {AcabValue : (AcabNode, {}, lambda c,p,u,ctx: c)})
        super(Trie, self).__init__(semantics)

        # Stores UUIDs -> Nodes
        self._all_nodes = WeakValueDictionary()

    def __str__(self):
        return self.print_trie()

    def __repr__(self):
        return "Trie: {}".format(len(self.get_nodes()))

    def __len__(self):
        return len(self.get_nodes())


    def add(self, path, data=None, semantics=None, **kwargs):
        """ Add the data to the leaf defined by path,
        """
        if semantics is None:
            semantics = self._semantics

        return semantics.add(self, [path], leaf_data=data, **kwargs)

    def remove(self, path, semantics=None):
        if semantics is None:
            semantics = self._semantics

        return semantics.delete(self, path)

    def query(self, query, ctxs=None, engine=None, semantics=None):
        use_semantics = semantics or self._semantics

        return use_semantics.query(self, query, ctxs=ctxs, engine=engine)

    def get_nodes(self, pred=None, explore=None):
        """ Get nodes passing a predicate function,
        exploring by an explore function:

        explore : [node] -> node -> [node]
        """
        assert(pred is None or callable(pred))
        assert(explore is None or callable(explore))
        nodes = []
        queue = list(self._root._children.values())
        visited = set()
        while queue:
            current = queue.pop(0)

            if current in nodes or current in visited:
                continue
            visited.add(current)

            if pred is None or pred(current):
                nodes.append(current)

            if explore is None:
                queue += [x for x in list(current._children.values())
                          if x not in visited]
            else:
                queue = explore(queue, current)

        return nodes

    def filter_candidates(self, candidates, match_func, semantics=None):
        if semantics is None:
            semantics = self._semantics

        return semantics.filter_candidates(self, candidates, match_func)

    def print_trie(self, join_str=None):
        raise DeprecationWarning("Use Print Semantics")
        # def_op = PrU.default_opts()
        # if join_str is not None:
        #     def_op['seq_join'] = join_str

        # output = self.to_sentences()
        # return "\n".join(sorted([x.pprint(def_op) for x in output]))

    def to_sentences(self, leaf_predicate=None):
        output = []
        queue = [([], x) for x in self._root]

        while bool(queue):
            curr_path, current_node = queue.pop(0)
            total_path = curr_path + [current_node.value]
            if not bool(current_node) or isinstance(current_node.value, AcabStatement):
                if leaf_predicate is None or leaf_predicate(current_node):
                    as_sentence = Sentence(total_path)
                    output.append(as_sentence)

            if bool(current_node):
                queue += [(total_path, x) for x in current_node]

        return output