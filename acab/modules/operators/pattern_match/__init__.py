from acab.abstract.interfaces.dsl_interface import DSL_Interface

from .pattern_match_op import PatternMatchOp
from . import pattern_match_parser as PMP


class MODULE(DSL_Interface):
    """ The Module Spec for base operators """

    def __init__(self):
        super().__init__()

    def assert_parsers(self, pt):
        pt.add("operator.transform.statement.pattern_match", PMP.parse_point)

    def query_parsers(self, pt):
        PMP.HOTLOAD_VALBIND << pt.query("valbind")
        PMP.HOTLOAD_VAR << pt.query("valbind")
        PMP.HOTLOAD_SEN << pt.query("sentence.param")
        PMP.HOTLOAD_QUERY << pt.query("query.clause")

    def init_strings(self):
        return []
