"""
A Trie Structure, using AcabNodes
"""
import logging as root_logger
from weakref import WeakValueDictionary, ref, proxy
from re import search

from acab.abstract.contexts import Contexts, CTX_OP
from acab.error.acab_base_exception import AcabBaseException
from acab.abstract.query import QueryComponent
from acab.abstract.sentence import Sentence
from acab.abstract.value import AcabStatement
from acab.abstract.printing import util as PrU
from acab.abstract.node import AcabNode
from acab.abstract.value import AcabValue

from acab.util import CONSTRAINT_S, AT_BIND_S

logging = root_logger.getLogger(__name__)


class Trie:

    def __init__(self, node_type=AcabNode):
        self._root = node_type.Root()
        self._node_type = node_type
        # Stores UUIDs -> Nodes
        self._all_nodes = WeakValueDictionary()

    def __str__(self):
        return self.print_trie()

    def __repr__(self):
        return "Trie: {}".format(len(self.get_nodes()))

    def __len__(self):
        return len(self.get_nodes())


    @property
    def root(self):
        return self._root


    def add(self, path, data=None, update=None, u_data=None, leaf_override=None):
        """ Add the data to the leaf defined by path,
        updating each node along the way using update and u_data
        use leaf_override to add more specific leaves
        """
        if leaf_override is None:
            leaf_override = self._node_type
        assert(issubclass(leaf_override, self._node_type))

        wrapped_path = [self._node_type(x) for x in path[:-1]]
        wrapped_path.append(leaf_override(path[-1]))


        current = self._root
        current_path = []
        for x, y in zip(wrapped_path, path):
            current_path.append(x)
            if current.has_child(x):
                current = current.get_child(x)
                logging.debug("Trie: Retrieved: {}".format(current))
            else:
                current = current.add_child(x)
                logging.debug("Trie: Added: {}".format(current))
                self._all_nodes[current._uuid] = current
            if update is not None:
                update(current, y, current_path, u_data)

        current.set_data(data)

        return current

    def remove(self, path):
        query_result = self.query(path[:-1])
        if query_result is not None:
            query_result.remove_child(path[-1])


    def get_nodes(self, pred=None, explore=None):
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
                queue += explore(current)

        return nodes


    def print_trie(self, join_str=None):
        def_op = PrU.default_opts()
        if join_str is not None:
            def_op['join'] = join_str

        output = self.to_sentences()
        return "\n".join(sorted([x.pprint(def_op) for x in output]))

    def to_sentences(self):
        output = []
        queue = [([], x) for x in self._root]

        while bool(queue):
            curr_path, current_node = queue.pop(0)
            total_path = curr_path + [current_node.value]
            if not bool(current_node) or isinstance(current_node.value, AcabStatement):
                # if leaf or statement
                as_sentence = Sentence(total_path)
                output.append(as_sentence)

            if bool(current_node):
                queue += [(total_path, x) for x in current_node]

        return output


    def query(self, path):
        """ Simple Query: Given a basic path,
        either return the leaf, or None """
        current = self._root
        for x in path:
            logging.debug("Searching {} for: {}".format(str(current), x))
            if current.has_child(x):
                current = current.get_child(x)
            else:
                return None
        return current

    def contextual_query(self, clause, contexts=None):
        """ Test a single clause,
        annotating contexts upon success and failure """
        assert(isinstance(clause, Sentence))
        if contexts is None:
            contexts = Contexts()

        logging.debug("Testing Clause: {}".format(repr(clause)))
        # Return to root unless clause has a head @ binding
        binding_val = None
        if clause[0].is_at_var:
            binding_val = clause[0].value

        contexts.force_node_position(target=self.root, binding=binding_val)

        # Go down from the root by query element:
        # For each word of the clause sentence, eg: a. in a.b.word
        collapse_on = set()
        for word in clause:
            logging.info("Testing node: {}".format(repr(word)))
            logging.info("Current Contexts: {}".format(len(contexts)))
            if not bool(contexts):
                break

            if word.is_at_var:
                continue

            # test each active alternative
            annotations = self._continue_query(word, contexts)

            if CTX_OP.collapse in annotations and word.is_var:
                collapse_on.add(word.name)

            # TODO add in context growth restrictions?

        if bool(collapse_on):
            contexts.collapse(collapse_on)

        return contexts

    def _continue_query(self, query_word, query_context):
        """ query word, with a sequence of tests,
        in all available bind groups, BFS manner """
        assert(not query_word.is_at_var)
        engine = query_context._engine
        alphas, betas, regexs, annotations = split_constraints(query_word)
        data_set = {x : d for x,d in enumerate(query_context.pairs())}
        pairs  = enumerate(query_context.pairs())
        query_context.clear()

        potentials = [(i, d[0], passing) for i,d in pairs for passing in retrieve_potentials(query_word, d)]
        # Apply Tests
        passing = [match_regexs(n, regexs, d, i) for i,d,n in potentials
                   if test_alphas(n, alphas, d, engine=engine)
                   and test_betas(n, betas, d, engine=engine)]

        to_add = [add_var_to_context(i, query_word, d, n) for i,d,n in passing if n is not None]

        query_context.append(*to_add, fail_dict=data_set)
        return annotations


    def match_as_pattern(self, possible_matches, match_func):
        """ Given a trie/node of possible matches, return only actual matches,
        Treating self as the pattern
        """
        if isinstance(possible_matches, Trie):
            possible_matches = possible_matches.root

        if not isinstance(possible_matches, AcabNode):
            raise AcabBaseException()

        final_matches = []
        pattern_nodes = list(possible_matches._children.values())
        # (current pattern position, available choices, match state)
        queue = [(x, pattern_nodes, []) for x in self.root._children.values()]

        while bool(queue):
            current, available_nodes, match_state = queue.pop(0)

            matching_nodes = match_func(current, available_nodes)
            for node in matching_nodes:
                next_match_state = match_state + [(current, node)]
                next_available = list(node._children.values())

                if bool(current):
                    next_patterns = list(current._children.values())
                    queue += [(x, next_available, next_match_state) for x in next_patterns]
                else:
                    final_matches.append(next_match_state)

        return final_matches




####################
# Utilities
def retrieve_potentials(query_word, pair):
    potentials = []
    data, node = pair
    # Handle query on var
    if query_word.is_var and query_word.name not in data:
        potentials = node._children.values()
    elif query_word.is_var:
        assert(query_word.name in data)
        value = data[query_word.name]
        if value in node:
            potentials.append(node.get_child(value))

    elif query_word in node:
        potentials.append(node.get_child(query_word))


    return potentials

def add_var_to_context(i, query_word, new_data, passing_node):
    assert(isinstance(query_word, AcabValue))
    assert(isinstance(passing_node, AcabNode))

    if query_word.is_var:
        new_data[query_word.name] = passing_node.value
        new_data[AT_BIND_S + query_word.name] =  passing_node

    return (i, new_data, passing_node)


def match_regexs(node, regexs, data, i):
    invalidated = False
    new_data = {}
    for regex in regexs:
        result = search(regex._params[0].value, node.name)
        if result is None:
            invalidated = True
            break

        for k, v in result.groupdict().items():
            if k not in data:
                new_data[k] = v
            elif data[k] != v:
                invalidated = True
                break

    if invalidated:
        node = None
        final_data = None
    else:
        final_data = data.copy()
        final_data.update(new_data)

    return (i, final_data, node)

def split_constraints(word):
    """ Split tests into (alphas, betas, regexs) """
    if CONSTRAINT_S not in word._data:
        return ([], [], [], set())

    comps = [x for x in word._data[CONSTRAINT_S] if isinstance(x, QueryComponent)]
    others = set([x for x in word._data[CONSTRAINT_S] if not isinstance(x, QueryComponent)])
    alphas = []
    betas = []
    regexs = []
    for c in comps:
        if c.is_regex_test:
            regexs.append(c)
        elif c.is_alpha_test:
            alphas.append(c)
        else:
            betas.append(c)

    return (alphas, betas, regexs, others)


def test_alphas(node, comps, data=None, engine=None):
    """ Run alpha tests against word retrieved value """
    return all([x(node, data=data, engine=engine) for x in comps])

def test_betas(node, comps, data=None, engine=None):
    """ Run word beta tests against word retrieved value, with supplied bindings """
    return all([x(node, data=data, engine=engine) for x in comps])
