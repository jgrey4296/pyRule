import unittest
import logging
from test_context import pyRule
import pyRule.trie as T
import pyRule.trie.TransformParser as TP
import pyRule.trie.ActionParser as AP
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
        result = self.e.query('.a.b.c?')
        self.assertTrue(bool(result))

    def test_query_fail(self):
        self.assertFalse(self.e.query('.a.b.c?'))

    def test_query_fail_with_asserted_facts(self):
        self.e.add('.a.b.c, .a.b.d')
        result = self.e.query('.a.b.c?, .a.b.e?')
        self.assertFalse(self.e.query('.a.b.c?, .a.b.e?'))

    def test_query_with_binds(self):
        self.e.add('.a.b.c, .a.b.d, .a.d.c')
        self.assertTrue(self.e.query('.a.b.$x?, .a.d.$x?'))

    def test_query_with_binds_fail(self):
        self.e.add('.a.b.c, .a.b.d, .a.d.e')
        self.assertFalse(self.e.query('.a.b.$x?, .a.d.$x?'))
        
    def test_multi_assert(self):
        self.e.add('.a.b.c, .a.b.d, .a.b.e')
        self.assertEqual(len(self.e._trie._root._reconstruct()), 3)
        self.assertTrue(self.e.query('.a.b.c?, .a.b.d?, .a.b.e?'))

    def test_multi_retract(self):
        self.e.add('.a.b.c, .a.b.d, .a.b.e')
        self.assertEqual(len(self.e._trie._root._reconstruct()), 3)
        self.e.retract('.a.b.e, .a.b.d')
        self.assertEqual(len(self.e._trie._root._reconstruct()), 1)

    def test_multi_clause_query(self):
        self.e.add('.a.b.c, .a.b.d, .a.b.e')
        result = self.e.query('.a.b.c?, .a.b.d?, .a.b.e?')
        self.assertTrue(result)
        
    def test_rule_registration(self):
        self.assertEqual(len(self.e._rules), 0)
        self.e.registerRules(".a.test.rule:\nend")
        self.assertEqual(len(self.e._rules), 1)
        self.e.registerRules(".a.second.rule:\nend")
        self.assertEqual(len(self.e._rules), 2)

    def test_rule_registration_overwrite(self):
        self.assertEqual(len(self.e._rules), 0)
        self.e.registerRules(".a.test.rule:\nend")
        self.assertEqual(len(self.e._rules), 1)
        self.e.registerRules(".a.test.rule:\nend")
        self.assertEqual(len(self.e._rules), 1)
    

    def _test_register_action(self):
        self.assertEqual(len(self.e._custom_actions), 0)
        self.e.register_action("Test_Func", lambda e, p: logging.info("called"))
        self.assertEqual(len(self.e._custom_actions), 1)
        self.assertTrue(True)

    def test_run_transform(self):
        stub_ctx = T.Contexts.initial(None)
        stub_ctx[0]['a'] = 2
        stub_ctx[0]['b'] = 4

        stub_transform = TP.parseString('$a + 20, $b * 2')
        
        result = self.e._run_transform(stub_ctx, stub_transform)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['a'], 22)
        self.assertEqual(result['b'], 8)

    def test_run_transform_rebind(self):
        stub_ctx = T.Contexts.initial(None)
        stub_ctx[0]['a'] = 2
        stub_ctx[0]['b'] = 8

        stub_transform = TP.parseString('$a + 20 -> $q, $b * $a -> $w')
        result = self.e._run_transform(stub_ctx, stub_transform)
        self.assertIsInstance(result, dict)
        self.assertEqual(result['a'], 2)
        self.assertEqual(result['b'], 8)
        self.assertEqual(result['q'], 22)
        self.assertEqual(result['w'], 16)
        
    def test_run_assert_action(self):
        actions = AP.parseString("+(.a.b.c)")
        self.assertFalse(self.e.query(".a.b.c?"))
        self.e._run_actions({},actions)
        self.assertTrue(self.e.query(".a.b.c?"))

    def test_run_retract_action(self):
        actions = AP.parseString("-(.a.b.c)")
        self.e.add(".a.b.c")
        self.assertTrue(self.e.query(".a.b.c?"))
        self.e._run_actions({}, actions)
        self.assertFalse(self.e.query(".a.b.c?"))
        self.assertTrue(self.e.query("~.a.b.c?"))

    def test_run_assert_multi_action(self):
        actions = AP.parseString("+(.a.b.c), +(.a.b.d)")
        self.assertFalse(self.e.query(".a.b.c?, .a.b.d?"))
        self.assertTrue(self.e.query("~.a.b.c?, ~.a.b.d?"))
        self.e._run_actions({}, actions)
        self.assertTrue(self.e.query(".a.b.c?, .a.b.d?"))

    def test_run_mixed_multi_action(self):
        actions = AP.parseString("+(.a.b.c), -(.a.b.d)")
        self.e.add(".a.b.d")
        self.assertTrue(self.e.query("~.a.b.c?, .a.b.d?"))
        self.e._run_actions({}, actions)
        self.assertTrue(self.e.query(".a.b.c?, ~.a.b.d?"))

    def test_run_bound_assert_action(self):
        data = {"x": "blah"}
        actions = AP.parseString("+(.a.b.$x)")
        self.assertTrue(self.e.query("~.a.b.blah?"))
        self.e._run_actions(data, actions)
        self.assertTrue(self.e.query(".a.b.blah?"))

    def test_run_bound_retract_action(self):
        data = {"blah" : "bloo"}
        actions = AP.parseString("-(.a.$blah.c)")
        self.e.add(".a.bloo.c")
        self.assertTrue(self.e.query(".a.bloo.c?"))
        self.e._run_actions(data, actions)
        self.assertTrue(self.e.query("~.a.bloo.c?, .a.bloo?"))

    def test_run_mixed_bound_actions(self):
        data = {"blah": "bloo"}
        actions = AP.parseString("+(.a.$blah), -(.b.$blah)")
        self.e.add(".b.bloo")
        self.assertTrue(self.e.query(".b.bloo?"))
        self.e._run_actions(data, actions)
        self.assertTrue(self.e.query(".a.bloo?, ~.b.bloo?"))

    def test_register_and_run_entire_rule(self):
        self.e.registerRules(".a.test.rule:\n.a.$x?\n\n$x + 20 -> $y\n\n+(.b.$y)\nend")
        self.e.add(".a.20")
        self.assertTrue(self.e.query(".a.20?, ~.b.40?"))
        self.e._run_rules()
        self.assertTrue(self.e.query(".a.20?, .b.40?"))
        
        
        
        
if __name__ == "__main__":
    LOGLEVEL = logging.INFO
    logFileName = "log.engine_tests"
    logging.basicConfig(filename=logFileName, level=LOGLEVEL, filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.WARN)
    logging.getLogger().addHandler(console)
    unittest.main()
    #reminder: user logging.getLogger().setLevel(logging.NOTSET) for log control
