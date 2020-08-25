import pyparsing as pp

from acab.abstract.parsing import util as PU
from acab.abstract.query import QueryComponent
from acab.abstract.value import AcabValue
from acab.abstract.sentence import Sentence
from acab.config import AcabConfig

from . import query_operators as QO

util = AcabConfig.Get()
TAG_S = util("Parsing.Structure", "TAG_S")
CONSTRAINT_S = util("Parsing.Structure", "CONSTRAINT_S")


def construct_tag_query(toks):
    assert(TAG_S in toks)
    tags = [x[1] for x in toks[TAG_S]]

    tag_op_path = Sentence.build([QO.HasTag.__name__])
    return (CONSTRAINT_S, QueryComponent(tag_op_path, param=tags))


tagList = PU.N(TAG_S, pp.delimitedList(PU.tagName, delim=","))

tagList.setParseAction(construct_tag_query)
