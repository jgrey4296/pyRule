"""
The combined engine of underlying trie based working memory,
with support for transforms and actions
"""
import logging as root_logger
from os.path import exists, expanduser
from os.path import abspath
import pyparsing as pp

from acab.error.acab_parse_exception import AcabParseException
from acab.abstract.engine import Engine
from acab.working_memory.trie_wm.trie_working_memory import TrieWM
from acab.working_memory.trie_wm.parsing import TotalParser as TotalP

logging = root_logger.getLogger(__name__)


class TrieEngine(Engine):
    """ The Engine for an Agent.
    Holds a working memory, with rules, keeps track of proposed actions
    and the history of the agent. Performs actions that are registered
    """

    def __init__(self, modules=None, path=None, init=None):
        super().__init__(TrieWM, modules=modules, path=path, init=init)

    def load_file(self, filename):
        """ Given a filename, read it, and interpret it as an EL DSL string """
        assert(isinstance(filename, str))
        filename = abspath(expanduser(filename))
        logging.info("Loading: {}".format(filename))
        assert exists(filename), filename
        with open(filename) as f:
            # everything should be an assertion
            try:
                assertions = TotalP.parseFile(f)
            except pp.ParseException as exp:
                print("-----")
                print(str(exp))
                print(exp.markInputline())
                print("File Not Asserted into WM")
                return False

            # Assert facts:
            for x in assertions:
                logging.info("File load assertions: {}".format(x))
                self.add(x)

        return True