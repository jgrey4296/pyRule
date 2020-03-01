""" The Core Trie Data Structure base """
import logging as root_logger
from .nodes.fact_node import FactNode
from py_rule.abstract.contexts import Contexts
from py_rule.abstract.working_memory import WorkingMemory
from py_rule.abstract.query import Query
from py_rule.abstract.sentence import Sentence
from py_rule.abstract.trie.trie import Trie
from py_rule.error.pyrule_operator_exception import PyRuleOperatorException
from . import matching
from .parsing import FactParser as FP
from .parsing import QueryParser as QP
from .parsing import ActionParser as AP
from .parsing import TransformParser as TP
from .parsing import TotalParser as TotalP
logging = root_logger.getLogger(__name__)


class TrieWM(WorkingMemory):
    """ A Trie based working memory"""

    def __init__(self, init=None):
        """ init is a string of assertions to start the fact base with """
        super().__init__()
        self._internal_trie = Trie(FactNode)
        self._last_node = self._internal_trie._root
        if init is not None:
            self.add(init)

    def __eq__(self, other):
        if isinstance(other, TrieWM):
            return self._internal_trie._root == other._internal_trie._root
        elif isinstance(other, Trie):
            return self._internal_trie._root == other._root
        else:
            raise PyRuleOperatorException("Incorrect Eq arg: {}".format(type(other)))

    def add(self, s):
        """ Assert multiple facts from a single string """
        if isinstance(s, str):
            rules, assertions = TotalP.parseString(s)
            # TODO Retract negated sentences
            for x in assertions:
                self._assert_sentence(x)
        elif isinstance(s, Sentence):
            self._assert_sentence(s)
        else:
            raise PyRuleParseException("Unrecognised addition target: {}".format(type(s)))

    def retract(self, s):
        """ Retract multiple facts from a single string
        Just handles simple sentences, not complex statements
        """
        if isinstance(s, str):
            parsed = FP.parseString(s)
            for x in parsed:
                self._retract_sentence(x)
        elif isinstance(s, Sentence):
            self._retract_sentence(s)
        else:
            raise PyRuleParseException("Unrecognised retract target: {}".format(type(s)))

    def query(self, s):
        """ Query a string """
        if isinstance(s, str):
            query = QP.parseString(s)
            return self._query_sentence(query)
        elif isinstance(s, Sentence):
            return self._query_sentence(s)
        else:
            raise PyRuleParseException("Unrecognised query target: {}".format(type(s)))

    def __str__(self):
        return str(self._internal_trie)

    def _insert_into_values_parser(self, parser):
        FP.OTHER_VALS << parser

    def _insert_into_statement_parser(self, parser):
        TotalP.OTHER_STATEMENTS << parser

    def _build_operator_parser(self):
        """ Trigger the building of operators,
        *after* modules have been loaded
        """
        AP.build_operators()
        QP.build_operators()
        TP.build_operators()

    # Internal Methods:
    def _assert_sentence(self, sen):
        """ Assert a sentence of chained facts """
        assert (isinstance(sen, Sentence)), sen
        self._clear_last_node()
        for newNode in sen:
            self._last_node = self._last_node.insert(newNode)

        self._last_node._set_dirty_chain()

    def _retract_sentence(self, sen):
        """ Retract everything after the end of a sentence """
        assert(isinstance(sen, Sentence))
        # go down to the child, and remove it
        self._clear_last_node()
        factList = sen._words[:]
        lastInList = factList.pop()

        for node in factList:
            self._last_node = self._last_node.get(node)
            if self._last_node is None:
                return

        self._last_node.delete_node(lastInList)

    def _query_sentence(self, query):
        """ Query a TrieQuery instance """
        assert(isinstance(query, Query))
        self._clear_last_node()
        initial_context = Contexts.initial(self._internal_trie._root)
        return self._internal_query(query, initial_context)

    def _clear_last_node(self):
        """ Reset internal memory to point to the root.
        currently only used for retraction
        """
        self._last_node = self._internal_trie._root

    def _internal_query(self, query, ctxs):
        """ Go down the trie, running each test as necessary
        annotating contexts as necessary
        """
        contexts = ctxs
        pos, neg = query.split_clauses()

        logging.debug("Testing clauses: {} {}".format(len(pos), len(neg)))
        for clause in pos:
            reset_start_contexts = contexts.set_all_alts(self._internal_trie._root)
            (updated_contexts, failures) = self._match_clause(clause,
                                                              reset_start_contexts)
            if bool(clause._fallback):
                # add all failures back in, with the default value
                for d in failures:
                    for bindTarget, val in clause._fallback:
                        d[bindTarget.value] = val
                updated_contexts._matches += [(x, self._internal_trie._root) for x in failures]

            if bool(updated_contexts) is False:
                logging.debug("A positive clause is false")
                contexts = updated_contexts
                break
            contexts = updated_contexts

        for negClause in neg:
            reset_start_contexts = contexts.set_all_alts(self._internal_trie._root)
            result, failures = self._match_clause(negClause, reset_start_contexts)
            logging.debug("neg result: {}".format(str(result)))
            if bool(result) is True:
                logging.debug("A Negative clause is true")
                contexts.fail()
                break

        return contexts

    def _match_clause(self, clause, contexts):
        """ Test a single clause, annotating contexts upon success and failure """
        assert(isinstance(clause, Sentence))
        logging.debug("Testing Clause: {}".format(repr(clause)))
        # early exit:
        if not contexts:
            return contexts
        currentContexts = contexts
        failures = []
        # Go down from the root by query element:
        # Failure at any point means don't add the updated context

        # For each part of the clause, ie: .a in .a.b.c
        for c in clause:
            logging.info("Testing node: {}".format(repr(c)))
            logging.info("Current Contexts: {}".format(len(currentContexts)))
            if len(currentContexts) == 0:
                break

            alphas, betas, regexs = c.split_tests()
            newContexts = Contexts()

            # test each  active alternative
            for (data, lastNode) in currentContexts._matches:
                tested = False
                newData = None
                newNode = None
                newBindings = []
                # compare non-bound value, returns (newNode, newData)?
                if not tested:
                    tested, newNode, newData = matching.non_bind_value_match(c, lastNode,
                                                                             betas,
                                                                             regexs, data)

                if not tested:
                    # compare already bound value, returns (newNode, newData)?
                    tested, newNode, newData = matching.existing_bind_match(c, lastNode,
                                                                            betas, regexs,
                                                                            data)

                if not tested:
                    # create new bindings as necessary, returns [(newNode, newData)]
                    newBindings = matching.create_new_bindings(c, lastNode,
                                                               alphas, betas,
                                                               regexs, data)

                if newData is not None:
                    newContexts.append((newData, newNode))
                elif bool(newBindings):
                    newContexts._matches += [x for x in newBindings if x[0] is not None]
                else:
                    failures.append(data.copy())

                # end of internal loop for an active alternative

            # all alternatives tested for this clause component, update and progress

            currentContexts = newContexts

        # every alternative tested for each clause component,
        # return the final set of contexts
        return (currentContexts, failures)