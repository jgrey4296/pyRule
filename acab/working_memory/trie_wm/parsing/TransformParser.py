""" Trie-based parser for the transform component of rules """
import logging as root_logger
import pyparsing as pp
from acab.abstract.transform import TransformComponent
from acab.abstract.transform import Transform, TransformOp
from acab.abstract.parsing import util as PU
from acab.working_memory.trie_wm import util as WMU
from acab.working_memory.trie_wm.parsing.FactParser import VALBIND, BASIC_SEN

logging = root_logger.getLogger(__name__)

# Builders:
def build_transform_component(toks):
    params = []
    position = 0
    if WMU.LEFT_S in toks:
        params += toks[WMU.LEFT_S][:]
        position = len(toks[WMU.LEFT_S])
    params += toks[WMU.RIGHT_S][:]


    rebind = toks[WMU.TARGET_S][0]
    return TransformComponent(toks[WMU.OPERATOR_S][0],
                              params, op_pos=position,
                              rebind=rebind)

def build_transform(toks):
    trans = Transform(toks[:])
    return (trans.type, trans)


# Hotloaded Transform Operators
HOTLOAD_TRANS_OP = pp.Forward()

# TODO need to add to this
HOTLOAD_TRANS_STATEMENTS = pp.Forward()

rebind = PU.ARROW + VALBIND
# TODO: extend transform to take partial transforms?
# transform: ( bind op val|bind -> bind)
transform_core = PU.N(WMU.LEFT_S, pp.ZeroOrMore(VALBIND)) \
    + PU.N(WMU.OPERATOR_S, PU.BSLASH + HOTLOAD_TRANS_OP) \
    + PU.N(WMU.RIGHT_S, PU.orm(VALBIND)) \
    + PU.N(WMU.TARGET_S, rebind)

transform_combined = pp.Or([transform_core, HOTLOAD_TRANS_STATEMENTS])

transforms = pp.delimitedList(transform_combined, delim=PU.DELIM)

transform_statement = PU.STATEMENT_CONSTRUCTOR(PU.TRANSFORM_HEAD,
                                               BASIC_SEN,
                                               transforms + PU.component_gap)

# Actions
transform_core.setParseAction(build_transform_component)
transforms.setParseAction(build_transform)

# NAMING
transform_core.setName("Transform_CORE")
transforms.setName("TransformPlural")
transform_statement.setName("TransformDefinition")

# parse_point = transforms.ignore(PU.COMMENT)
parse_point = transforms

# Main Parser:
def parseString(in_string):
    return parse_point.parseString(in_string)[0][1]