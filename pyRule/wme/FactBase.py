""" FactBase: The WME-based implementation of a knowledge base """
import IPython
from pyRule.Contexts import Contexts
from pyRule.Query import Query
from pyRule.wme.WMEClause import WMEClause
from pyRule.Comparisons import COMP_LOOKUP
from pyRule.utils import Bind
from .WME import WME

#todo: eq, str

class FactBase:
    """ Main class for WME based knowledge base """

    def __init__(self):
        self._wmes = []
        self._wmeDict = {}
        self._hashes = set()
        self._currentTime = 0

    def clear(self):
        self._wmes = []
        self._wmeDict = {}
        self._hashes = set()
        self._currentTime = 0

    def incTime(self):
        self._currentTime += 1

    def assertWME(self, *args):
        """ Put a fact into the knowledge base """
        outputData = []
        for possibleData in args:
            if not isinstance(possibleData, WME):
                wme = WME(possibleData, self._currentTime)
            else:
                wme = possibleData
            wmeHash = hash(wme)
            if wmeHash in self._hashes:
                raise Exception("Assert WME Failed: WME already asserted")
            self._wmes.append(wme)
            self._wmeDict[wmeHash] = wme
            self._hashes.add(wmeHash)
            assert(len(self._wmes) == len(self._hashes))
            outputData.append(wme)
        return outputData

    def retractWME(self, wme):
        """ Remove a fact from the knowledge base """
        if not isinstance(wme, WME):
            raise Exception("Retracting WME Failed: Not passed a WME")
        wmeHash = hash(wme)
        if wmeHash not in self._hashes:
            return 0
        self._wmes = [x for x in self._wmes if hash(x) != wmeHash]
        del self._wmeDict[wmeHash]
        self._hashes.remove(wmeHash)
        assert(len(self._wmes) == len(self._hashes))
        assert(len(self._wmeDict) == len(self._wmes))
        return 1

    def query(self, query):
        """ Given a query of clauses comprising:
        alpha, binding, and beta tests, run it and return
        any matching wmes and bindings """
        contexts = Contexts.initial(None)
        posClauses, negClauses = query.splitClauses()
        for clause in posClauses:
            #pass the clause and intermediate results through
            contexts = self._matchWMEs(clause, contexts)

        #then check negative clauses
        negContext = contexts
        for clause in negClauses:
            #test each negated clause,
            #fail the query if any pass
            negResponse = self._matchWMEs(clause, negContext)
            if negResponse:
                contexts.fail()
                break

        #contexts.verifyMatches(len(query))
        return contexts


    def _matchWMEs(self, clause, contexts):
        """ Internal match procedure.
        Searches all wmes, running alpha tests,
        then bindings, then beta comparisons,
        before adding passing wmes to the context """
        assert(isinstance(clause, WMEClause))
        #Early fail out
        if not contexts:
            return contexts

        (alphaTests, bindOps, betaTests, regexs) = clause.split_tests()
        passingContexts = Contexts()
        for wme in self._wmes:
            #Alpha Tests
            if not self._test_alpha(wme, alphaTests):
                continue

            #bind
            newContexts = self._bind_values(wme, bindOps, contexts)
            if not bool(newContexts):
                continue

            #Beta Tests
            passingContexts._alternatives += self._test_beta(wme,
                                                             newContexts,
                                                             betaTests)._alternatives
        return passingContexts

    def _bind_values(self, wme, bindOps, contexts):
        """ Add in a new binding to each context, unless it conflicts """
        newContexts = Contexts()
        failed_contexts = []
        for (data, matchedWME) in contexts._alternatives:
            newData = data.copy()
            newMatchedWMEs = matchedWME
            for (field, bindName) in bindOps:
                assert(isinstance(bindName, Bind))
                if field not in wme._data:
                    failed_contexts.append(newData)
                    break
                if bindName.value in newData and wme._data[field] != newData[bindName.value]:
                    failed_contexts.append(newData)
                    break
                newData[bindName.value] = wme._data[field]

            if not bool(failed_contexts):
                newMatchedWME = wme
                newContexts._alternatives.append((newData, newMatchedWME))
            else:
                continue

        return newContexts


    def _test_alpha(self, wme, alphaTests):
        """ Run alpha tests (intra-wme) """
        for (field, op, val) in alphaTests:
            assert(op in COMP_LOOKUP)
            opFunc = COMP_LOOKUP[op]
            if not field in wme._data:
                return False
            if not opFunc(wme._data[field], val):
                return False
        return True

    def _test_beta(self, wme, contexts, betaTests):
        """ Run beta (inter-wme) tests on a wme and context """
        newContexts = Contexts()
        for (data, matchedWME) in contexts._alternatives:
            failMatch = False
            newData = data.copy()
            newMatchedWME = matchedWME
            for (field, op, bindName) in betaTests:
                assert(op in COMP_LOOKUP)
                assert(isinstance(bindName, Bind))
                opFunc = COMP_LOOKUP[op]
                #compare wme to token
                if isinstance(field, Bind) and not opFunc(newData[field.value],
                                                          newData[bindName.value]):
                    failMatch = True
                    break
                elif (not isinstance(field, Bind)) and field not in wme._data:
                    failMatch = True
                    break
                elif (not isinstance(field, Bind)) and \
                     not opFunc(wme._data[field], newData[bindName.value]):
                    failMatch = True
                    break

            if not failMatch:
                newContexts._alternatives.append((newData, newMatchedWME))

        return newContexts

    def __len__(self):
        """ The number of wmes in the factbase """
        return len(self._hashes)
