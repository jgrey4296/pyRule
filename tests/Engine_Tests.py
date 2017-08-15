import unittest
import logging
from test_context import pyRule
import pyRule.trie as T
import pyRule.trie.TransformParser as TP
import IPython

class Engine_Tests(unittest.TestCase):
    
    def setUp(self):
        self.e = T.Engine()
          
        
    def tearDown(self):
        self.e = None
          
    #----------
    #use testcase snippets
    def test_init(self):
        self.assertIsNotNone(self.e)

    def test_assert(self):
        self.assertEqual(len(self.e._trie._root), 0)
        self.e.add('.a.b.c')
        self.assertEqual(len(self.e._trie._root), 1)

    def test_retract(self):
        self.e.add('.a.b.c')
        self.assertEqual(len(self.e._trie._root), 1)
        self.e.retract('.a')
        self.assertEqual(len(self.e._trie._root), 0)

    def test_query(self):
        self.e.add('.a.b.c')
        result = self.e.query('.a.b.c')
        self.assertTrue(bool(result))

    def test_multi_assert(self):
        self.e.add('.a.b.c, .a.b.d, .a.b.e')
        self.assertEqual(len(self.e._trie._root._reconstruct()), 3)
        

    def test_multi_retract(self):
        self.e.add('.a.b.c, .a.b.d, .a.b.e')
        self.assertEqual(len(self.e._trie._root._reconstruct()), 3)
        self.e.retract('.a.b.e, .a.b.d')
        self.assertEqual(len(self.e._trie._root._reconstruct()), 1)

    def test_multi_clause_query(self):
        self.e.add('.a.b.c, .a.b.d, .a.b.e')
        result = self.e.query('.a.b.c, .a.b.d, .a.b.e')
        self.assertTrue(result)
        
    def _test_rule_registration(self):
        self.assertTrue(True)

    def _test_register_action(self):
        self.assertTrue(True)

    def test_run_transform(self):
        stub_ctx = T.Contexts.initial(None)
        stub_ctx[0]['a'] = 2
        stub_ctx[0]['b'] = 4

        stub_transform = TP.parseStrings('($a + 20, $b * 2)')
        
        result = self.e._run_transform(stub_ctx, stub_transform)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['a'], 22)
        self.assertEqual(result['b'], 8)

    def test_run_transform_rebind(self):
        stub_ctx = T.Contexts.initial(None)
        stub_ctx[0]['a'] = 2
        stub_ctx[0]['b'] = 8

        stub_transform = TP.parseStrings('($a + 20 -> $q, $b * $a -> $w)')
        result = self.e._run_transform(stub_ctx, stub_transform)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['a'], 2)
        self.assertEqual(result['b'], 8)
        self.assertEqual(result['q'], 22)
        self.assertEqual(result['w'], 16)
        
    def _test_run_actions(self):
        self.assertTrue(True)
      

if __name__ == "__main__":
    LOGLEVEL = logging.INFO
    logFileName = "log.engine_tests"
    logging.basicConfig(filename=logFileName, level=LOGLEVEL, filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.WARN)
    logging.getLogger().addHandler(console)
    unittest.main()
    #reminder: user logging.getLogger().setLevel(logging.NOTSET) for log control
