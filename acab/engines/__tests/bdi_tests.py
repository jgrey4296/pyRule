import unittest
import logging
import acab.util as util
from acab.engines import bdi_engine as bdi
from os.path import join, isfile, exists, isdir, splitext, expanduser
from os.path import abspath, split
from os import listdir


@unittest.skip("Broken")
class BDI_TESTS(unittest.TestCase):

    def path(self, filename):
        return abspath(join(split(__file__)[0],
                            '..',
                            'testfiles',
                            'bdi',
                            filename))

    def setUpAgent(self, files):
        self.e = bdi.Agent("testAgent",
                           [self.path(x) for x in files])

    #----------
    def test_init(self):
        self.setUpAgent(["initial_load_test.trie"])
        self.assertIsNotNone(self.e)

    #BDI architecture to test:
    #1) addition / retraction of beliefs
    #2) addition / retraction of rules
    #3) addition / retraction of desires
    #4) generation / retraction of intentions
    #5) addition of actions
    #6) selection of actions by intention
    #7) firing of actions
    #8) updating of beliefs from actions
    #9) Logic Cycle


if __name__ == "__main__":
      #use python $filename to use this logging setup
# Setup root_logger:
    LOGLEVEL = root_logger.DEBUG
    LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
    root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

    console = root_logger.StreamHandler()
    console.setLevel(root_logger.INFO)
    root_logger.getLogger('').addHandler(console)
    logging = root_logger.getLogger(__name__)

    unittest.main()
    #reminder: user logging.getLogger().setLevel(logging.NOTSET) for log control