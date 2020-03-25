"""
Actions: Describes the *ENGINE AGNOSTIC* basic actions that a working memory can
perform, along with associated enums, and IR data structures
"""
from . import production_operator as PO
from py_rule.error.pyrule_operator_exception import PyRuleOperatorException
from py_rule import util as util
from py_rule.abstract.sentence import Sentence
import logging as root_logger

logging = root_logger.getLogger(__name__)


# Action function template:
class ActionOp(PO.ProductionOperator):
    """ Superclass of all Actions.
    Instantiation of subclasses auto-registers
    the action into ActionOp.op_list with an operator string
    """
    op_list = {}

    def __init__(self, num_params=2, infix=False):
        # Registers self with class name,
        # DSL later binds to an operator
        super().__init__(num_params=num_params, infix=False)
        if self._op_str not in ActionOp.op_list:
            ActionOp.op_list[self._op_str] = self

    def __call__(self, engine, params):
        raise NotImplementedError()

    def __str__(self):
        return self._op_str

    def __repr__(self):
        return "ActionOp: {}".format(str(self))


class ActionComponent(PO.ProductionComponent):
    """ The Core Action Class, holds an operator,
    and a list of values """


    def __init__(self, op_str, params):
        """ Create an action with an operator and values """
        assert all([isinstance(x, Sentence) for x in params]), params
        super(ActionComponent, self).__init__(op_str, params)

    def __str__(self):
        op = str(self._op)
        args = []
        for val in self._params:
            if isinstance(val, list):  # and isinstance(val[0], Node):
                args.append("".join([str(x) for x in val]))
            else:
                args.append(str(val))
        return "{}({})".format(op, ",".join(args))

    def __repr__(self):
        return "Action({})".format(str(self))

    def __call__(self, engine, data):
        # lookup op
        assert(self._op in ActionOp.op_list)
        opFunc = ActionOp.op_list[self._op]
        # get values from data
        values = self.get_values(data)
        # perform action op with data
        opFunc(engine, values)

    def verify_op(self):
        """ Check the Action is using a valid operator (ACT enum) """
        if self._op not in ActionOp.op_list.keys():
            raise AttributeError("Unrecognised Action: {}".format(self._op))

    def get_values(self, data):
        """ Output a list of bindings from this action """
        output = []
        for x in self._params:
            if isinstance(x, Sentence):
                output.append(x.expand_bindings(data))
            elif isinstance(x, list):  # and all([isinstance(y, Node) for y in x]):
                output.append([y.bind(data) for y in x])
            elif hasattr(x, '_data') and x._data[util.BIND_S]:
                if util.AT_BIND_S in x._data:
                    output.append(data[util.AT_BIND_S + x._value])
                else:
                    output.append(data[x._value])
            else:
                output.append(x)
        return output

    def expand_bindings(self, bindings):
        """ Expand stored bindings at interpret time
        ie: +(.a.b.$x) + { x : .a.b.c } -> +(.a.b.a.b.c)
        """
        new_values = []
        for x in self._params:
            if isinstance(x, Sentence):
                new_values.append(x.expand_bindings(bindings))
            else:
                new_values.append(x)
        return ActionComponent(self._op, new_values)

    def to_sentence(self):
        """ Return the action in canonical form """
        # eg : assert a.test  = assert -> a.test -> nil
        sen = Sentence([self._op] + self._params[:])
        return sen


class Action(PO.ProductionContainer):

    def __init__(self, clauses, params=None, type_str=util.ACTION_S):
        super(Action, self).__init__(clauses, type_str=type_str)
        self._params = []
        if params is not None:
            self._params += params

    def __str__(self):
        return ", ".join([str(x) for x in self._clauses])

    def __repr__(self):
        return "Action({})".format(str(self))

    def expand_bindings(self, bindings):
        """ Expand stored bindings """
        exp_clauses = []
        for clause in self._clauses:
            exp_clauses.append(clause.expand_bindings(bindings))

        return Action(exp_clauses, params=self._params)

    def value_string(self):
        return self._name
