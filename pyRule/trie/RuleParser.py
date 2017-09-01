import logging as root_logger
import pyparsing as pp
from .Rule import Rule
from . import FactParser as FP
from . import QueryParser as QP
from . import TransformParser as TP
from . import ActionParser as AP


import IPython
pp.ParserElement.setDefaultWhitespaceChars(' \t\r')

logging = root_logger.getLogger(__name__)

def build_rule(toks):
    name = toks.ruleName[:]
    if 'conditions' in toks:
        c = toks.conditions[0]
    else:
        c = None
    if 'transforms' in toks:
        t = toks.transforms[0]
    else:
        t = None
    if 'actions' in toks:
        a = toks.actions[:]
    else:
        a = []
    if 'tags' in toks:
        tags = toks.tags[:]
    else:
        tags = []
    return Rule(c, a, transform=t, name=name, tags=tags)
        
        
s = pp.Suppress
op = pp.Optional
opLn = s(op(pp.LineEnd()))
HASH = s(pp.Literal('#'))
emptyLine = s(pp.lineEnd + pp.lineEnd)

ruleName = FP.param_fact_string.copy().setResultsName('ruleName')
tagName = HASH + FP.NAME

tagList = (tagName + pp.ZeroOrMore(FP.COMMA + tagName) + emptyLine).setResultsName('tags')
conditions = (QP.clauses + emptyLine).setResultsName('conditions')
transforms = (TP.transforms + emptyLine).setResultsName('transforms')
actions = (AP.actions + s(pp.lineEnd)).setResultsName('actions')

rule = ruleName + FP.COLON + FP.sLn \
       + op(tagList) \
       + op(conditions) + op(transforms) + op(actions) \
       + FP.end

rules = rule + pp.ZeroOrMore(emptyLine + rule)


rule.setParseAction(build_rule)

def parseString(s):
    assert(isinstance(s, str))
    return rules.parseString(s)[:]


"""
meta rules:
add/remove/replace penumbra conditions
modify penumbra transforms
add/remove/replace penumbra actions
"""
