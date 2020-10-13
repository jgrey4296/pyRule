#!/usr/bin/env python
from re import Pattern
from acab.config import AcabConfig

from acab.abstract.core.type_base import TypeInstance


util = AcabConfig.Get()

def _maybe_wrap_str(semantics, value, current):

    return '"{}"'.format(current)

def _wrap_regex(semantics, value, current):
    if not isinstance(value.value, Pattern):
        return current

    val = "/{}/".format(current)
    return val


def _maybe_wrap_var(semantics, value, current):
    assert(isinstance(value, str))
    sym = semantics.get_alias("VAR_SYMBOL_S")
    if value.is_at_var:
        sym = semantics.get_alias("AT_VAR_SYMBOL_S")
    if value.is_var:
        return sym + current
    else:
        return curren


def _wrap_constraints(value, data):
    assert(isinstance(value, str))
    assert(isinstance(data, dict))

    constraints = []

    if data[VALUE_TYPE_S] not in OBVIOUS_TYPES:
        constraints.append(data[VALUE_TYPE_S])

    # Get registered data annotations:
    for x in REGISTERED_CONSTRAINTS:
        if x in data:
            if isinstance(data[x], list):
                constraints += data[x]
            else:
                constraints.append(data[x])

    result = value
    # Print the constraints
    if bool(constraints):
        cons_strs = ", ".join([pprint(x) for x in constraints])
        result += "({})".format(cons_strs)
    return result

def _modal_operator(semantics, value, current):
    modal_data_field = semantics.ask('MODAL_FIELD')
    if modal_data_field not in value._data:
        modal_str = semantics.get_alias("FALLBACK_MODAL_S")
    else:
        modal_str = semantics.get_alias(modal_data_field)

    return modal_str

def _wrap_rebind(value, rebind, is_sugar=False):
    arrow = "->"
    if rebind is None:
        return value
    if is_sugar:
        arrow = "=>"


    return "{} {} {}".format(value,
                             arrow,
                             pprint(rebind))

def _maybe_wrap_question(semantics, value, current):
    query_symbol = ""
    if value._data["QUERY_S"]:
        query_symol = semantics.get_alias("QUERY_SYMBOL_S")

    return "{}{}".format(current, query_symbol)

def _maybe_wrap_negation(semantics, value, current):
    neg_symbol = ""
    if "NEGATION_S" in value._data and value._data["NEGATION_S"]:
        neg_symbol = semantics.get_alias("NEGATION_SYMBOL_S")

    return "{}{}".format(neg_symbol, current)

def _wrap_fallback(semantics, the_list):
    assert(len(the_list)%2 == 0)

    the_vars = [x for i, x in enumerate(the_list) if i%2==0]
    the_vals = [x for i, x in enumerate(the_list) if i%2==1]

    joined = ", ".join(["{}:{}".format(x, y) for x, y
                        in zip(the_vars, the_vals)])

    return " || {}".format(joined)

def _wrap_tags(value, tags, sep=TAB_S):
    tags_s = [str(x) for x in tags]
    return "{}{}{}\n\n".format(value, sep, ", ".join(sorted([TAG_SYMBOL_S + x for x in tags_s])))

def _maybe_wrap(value, maybeNone, sep=None):
    if maybeNone is None:
        return (value, False)
    return (value + sep + maybeNone.pprint(), True)

def _wrap_colon(value, newline=False):
    tail = ""
    if newline:
        tail = "\n"

    return "{}:{}".format(value, tail)

def _wrap_end(value, newline=False):
    if newline:
        return "{}\n{}\n".format(value, END_S)
    else:
        return "{}{}\n".format(value, END_S)

def _wrap_var_list(val, the_vars, newline=False):
    head = ""
    if newline:
        head = "\n"
    return "{}{}{}| {} |\n".format(val, head, TAB_S, ", ".join([_wrap_var(x.name) for x in the_vars]))