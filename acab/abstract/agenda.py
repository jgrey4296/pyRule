""""
Agendas are special cases of rules
"""
from enum import Enum
from acab import util
from acab.util import NAME_S, STATEMENT_S, TYPE_DEC_S, QUERY_S, TRANSFORM_S, ACTION_S
from acab.abstract.rule import Rule
from acab.abstract.production_operator import ProductionOperator, ProductionContainer
from acab.abstract.printing import util as PrU

RELATION_E = Enum('Agenda_Relation', 'ONE MANY')

class Agenda(Rule):
    """
    Takes a set of potential rule activations
    and applys a transform, filter, or other function on them
    """

    RETURN_NAME_S = "__agenda_return_name__"

    def __init__(self,
                 query=None,
                 transform=None,
                 action=None,
                 name="AnonAgenda"):

        super(Agenda, self).__init__(query=query,
                                     transform=transform,
                                     action=action,
                                     name=name,
                                     type_str=util.AGENDA_HEAD_S)
        # Whether the agenda expands or constrains proposals
        self._relation_type = (None, None)


    def __call__(self, ctxs=None, engine=None):
        """ Runs an agenda rule on activated rules """
        assert(isinstance(ctxs, list))
        agenda_settings = super(Agenda, self).__call__(ctxs=ctxs, engine=engine)

        assert(len(agenda_settings) == 1)
        settings = agenda_settings[0][0]

        # Enact agenda
        resulting_ctxs = self._action(settings, engine)
        return resulting_ctxs[0][Agenda.RETURN_NAME_S]


# Utility construction function for parser
def make_agenda(toks):
    # Get Conditions
    if QUERY_S in toks:
        c = toks[QUERY_S][0][1]
        assert(isinstance(c, ProductionContainer))
    else:
        c = None

    # Get Transform
    if TRANSFORM_S in toks:
        t = toks[TRANSFORM_S][0][1]
        assert(isinstance(t, ProductionContainer))
    else:
        t = None

    # Get Action
    if ACTION_S in toks:
        a = toks[ACTION_S][0][1]
        assert(isinstance(a, ProductionContainer))
    else:
        a = None

    # make the agenda
    the_agenda = Agenda(query=c, transform=t, action=a)

    return  (the_agenda.type, the_agenda)


PrU.register_statement({util.AGENDA_HEAD_S : util.AGENDA_HEAD_S})
