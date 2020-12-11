"""
Defintions for Core Transform Operators
"""
from re import sub
from acab.abstract.containers.production_abstractions import ProductionOperator

class RegexOp(ProductionOperator):

    def __call__(self, value, pattern, replacement, data=None, engine=None):
        """ Substitute value pattern with value value from passed in data
        value : the replacement
        pattern: the pattern

        sub(pattern, replacement, string, count, flags)
        """
        return sub(pattern, replacement, value)


class FormatOp(ProductionOperator):

    def __call__(self, value, data=None, engine=None):
        """ Use str.format variant with value data dictionary
        Replaces variables in the string with bound values
        """
        return value.format(**data)
