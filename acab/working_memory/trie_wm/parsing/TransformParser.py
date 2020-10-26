""" Trie-based parser for the transform component of rules """
import logging as root_logger
import pyparsing as pp

from acab.abstract.parsing import util as PU
from acab.abstract.parsing import funcs as Pfunc
from acab.abstract.parsing.consts import ARROW, DOUBLEBAR, COLON, COMMA, COLON, DELIM, component_gap
from acab.abstract.parsing.consts import N, NG, zrm, TRANSFORM_HEAD
from acab.working_memory.trie_wm.parsing import util as WMPU

from acab.working_memory.trie_wm.parsing.util import RIGHT_S, OPERATOR_S, TARGET_S, LEFT_S
from acab.working_memory.trie_wm.parsing.util import build_transform_component, build_transform

from acab.working_memory.trie_wm import util as WMU
from acab.working_memory.trie_wm.parsing.FactParser import BASIC_SEN, PARAM_SEN, op_path

from acab.config import AcabConfig

logging = root_logger.getLogger(__name__)

# Hotloaded Transform Operators
HOTLOAD_TRANS_OP = pp.Forward()
HOTLOAD_TRANS_STATEMENTS = pp.Forward()
HOTLOAD_TRANS_OP.setName("Transform_Op")
HOTLOAD_TRANS_STATEMENTS.setName("Transform_Statement")

rebind = ARROW + WMPU.VALBIND
rebind.setName("Rebind")

# TODO: extend transform to take partial transforms?
# transform: ( bind op val|bind -> bind)

vals = N(RIGHT_S, zrm(PARAM_SEN))
# vals.addCondition(lambda toks: all([isinstance(x, Sentence) for x in toks]))

transform_core = N(OPERATOR_S, op_path) \
    + vals \
    + N(TARGET_S, rebind)

transform_sugar = NG(LEFT_S, PARAM_SEN) \
    + N(OPERATOR_S, HOTLOAD_TRANS_OP) \
    + vals \
    + N(TARGET_S, rebind)

transform_combined = pp.Or([transform_core, HOTLOAD_TRANS_STATEMENTS, transform_sugar])

transforms = pp.delimitedList(transform_combined, delim=DELIM)

transform_statement = Pfunc.STATEMENT_CONSTRUCTOR(TRANSFORM_HEAD,
                                                  BASIC_SEN,
                                                  transforms + component_gap)

# Actions
transform_core.setParseAction(build_transform_component)
transform_sugar.addParseAction(build_transform_component)
transforms.setParseAction(build_transform)

# NAMING
transform_core.setName("Transform_CORE")
transforms.setName("TransformPlural")
transform_statement.setName("TransformDefinition")

parse_point = transforms

# Main Parser:
def parseString(in_string):
    return parse_point.parseString(in_string)[0][1]
