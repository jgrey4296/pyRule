""" Trie-based parser for constructing queries """
import logging as root_logger
import pyparsing as pp
import py_rule.abstract.comparison as C
from py_rule.abstract.query import Query
from py_rule.abstract.sentence import Sentence
from .FactParser import COMMA, PARAM_CORE, BIND, COLON, N, TYPEDEC_CORE, param_fact_string

pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

logging = root_logger.getLogger(__name__)

NOT_IDEN = 'NOT'
COMP_IDEN = 'comparison'
RULEBIND_IDEN = 'rulebind'


def build_constraint_list(toks):
    return ("constraints", toks[:])

def build_comparison(toks):
    return C.Comparison(toks.op, value=toks.value)

def build_clause(toks):
    #detect negation and annotate the clause with it
    if 'fallback_bindings' in toks:
        fallback_toks = toks.fallback_bindings[:]
    else:
        fallback_toks = None
    if NOT_IDEN in toks:
        if fallback_toks is not None:
            raise Exception("Fallback bindings in negated clauses don't make sense")
        return Sentence(toks.main_clause[:], negated=True, is_query=True)
    else:
        return Sentence(toks.main_clause[:], fallback=fallback_toks, is_query=True)


s = pp.Suppress
op = pp.Optional
opLn = s(op(pp.LineEnd()))

OPAR = s(pp.Literal('('))
CPAR = s(pp.Literal(')'))
QMARK = s(pp.Literal('?'))

COMP_OP = pp.Forward()

def build_operators():
    if COMP_OP.expr is None:
        OP_STRS = [x for x in C.CompOp.op_list.keys()]
        COMP_OP << pp.Or([pp.Literal(x) for x in OP_STRS])

NOT = N(NOT_IDEN, pp.Literal('~'))
SLASH = s(pp.Literal('/'))
DOUBLEBAR = s(pp.Literal('||'))
META = s(pp.Literal('^'))

COMP_Internal = N("op", COMP_OP) + N("value", PARAM_CORE(end=True))

#defined earlier to work with named copies
COMP_Internal.setParseAction(build_comparison)


#TODO: add comparison features for testing rule components
#ie: has tag, has penumbral conditions,
#has penumbral actions
ruleBind = META + PARAM_CORE(end=True)

comp_or_typedef = pp.Or([N("comp", COMP_Internal), N("typedec", TYPEDEC_CORE), N("rulebind", ruleBind)])
constraints = comp_or_typedef + op(pp.OneOrMore(COMMA + comp_or_typedef))
constraints.setParseAction(build_constraint_list)

assignment = BIND + COLON + param_fact_string
assignmentList = assignment + pp.ZeroOrMore(COMMA + assignment)
fallback = DOUBLEBAR + assignmentList

#core component of a query, a modified param_fact_string
QueryCore = PARAM_CORE(constraints)
QueryCore_end = PARAM_CORE(constraints, end=True)

#Core Query Chain
clause = op(NOT) + N("main_clause", pp.ZeroOrMore(QueryCore) + QueryCore_end) \
         + QMARK + N("fallback_bindings", op(fallback))

clauses = clause + pp.ZeroOrMore(COMMA + clause)

#Actions
clause.setParseAction(build_clause)
clauses.setParseAction(lambda toks: Query(toks[:]))

#assignment:
assignment.setParseAction(lambda toks: (toks[0][1], toks[1]))


#Main parser:
def parseString(in_string):
    """ .a.b(>20)!d.$X, ... -> Query """
    return clauses.parseString(in_string)[0]
