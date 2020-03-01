import unittest
import logging
from test_context import py_rule
from py_rule.working_memory.trie_wm import util as KBU
from py_rule.working_memory.trie_wm.parsing import RuleParser as RP
from py_rule.working_memory.trie_wm.parsing import FactParser as FP
from py_rule.modules.standard_operators.operator_module import OperatorSpec
from py_rule.abstract.rule import Rule
from py_rule.abstract.sentence import Sentence
from py_rule.abstract.query import Query

class Trie_Rule_Parser_Tests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os = OperatorSpec()
        os._construct_comp_ops()
        os._construct_action_ops()
        os._construct_transform_ops()
        RP.build_operators()

    def setUp(self):
            return 1

    def tearDown(self):
            return 1

    #----------
    #use testcase snippets
    def test_init(self):
            self.assertIsNotNone(RP)

    def test_name_empty_rule_parse(self):
            result = RP.parseString("a.rule:\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertEqual(str(result[0][1]._name), "a.rule")

    def test_multi_empty_rules(self):
            result = RP.parseString("a.rule:\nend\n\na.second.rule:\nend")
            self.assertEqual(len(result),2)
            self.assertTrue(all([isinstance(x[1],Rule) for x in result]))

    def test_rule_with_query(self):
            result = RP.parseString("a.rule:\na.b.c?\n\nend")
            self.assertEqual(len(result),1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertIsNotNone(result[0][1]._query)
            self.assertIsInstance(result[0][1]._query, Query)

    def test_rule_with_multi_clause_query(self):
            result = RP.parseString("a.rule:\na.b.c?,\na.b.d?\n\nend")
            self.assertEqual(len(result),1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertIsNotNone(result[0][1]._query)
            self.assertIsInstance(result[0][1]._query, Query)
            self.assertEqual(len(result[0][1]._query), 2)

    def test_rule_with_multi_clauses_in_one_line(self):
            result = RP.parseString("a.rule:\na.b.c?, a.b.d?\n\nend")
            self.assertEqual(len(result),1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertIsNotNone(result[0][1]._query)
            self.assertIsInstance(result[0][1]._query, Query)
            self.assertEqual(len(result[0][1]._query), 2)

    def test_rule_with_binding_query(self):
            result = RP.parseString("a.rule:\na.b.$x?\n\nend")
            self.assertEqual(len(result),1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertIsNotNone(result[0][1]._query)
            self.assertIsInstance(result[0][1]._query, Query)
            self.assertEqual(len(result[0][1]._query), 1)

    @unittest.skip("numbers have been deprecated")
    def test_rule_with_transform(self):
            result = RP.parseString("a.rule:\n$x + 20 -> $y\n\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertIsNone(result[0][1]._query)
            self.assertIsNotNone(result[0][1]._transform)

    @unittest.skip("numbers have been deprecated")
    def test_rule_with_multiple_transforms(self):
            result = RP.parseString("a.rule:\n $x + 20 -> $y, $y - 20\n\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertIsNone(result[0][1]._query)
            self.assertIsNotNone(result[0][1]._transform)

    @unittest.skip("numbers have been deprecated")
    def test_rule_with_multiple_transforms_on_single_line(self):
            result = RP.parseString("a.rule:\n$x + 20 -> $y,$y - 20\n\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertIsNone(result[0][1]._query)
            self.assertIsNotNone(result[0][1]._transform)

    def test_rule_with_actions(self):
            result = RP.parseString("a.rule:\n+(a.b.c)\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertIsNone(result[0][1]._query)
            self.assertIsNone(result[0][1]._transform)
            self.assertEqual(len(result[0][1]._actions), 1)

    def test_multi_action_rule(self):
            result = RP.parseString("a.rule:\n+(a.b.c),\n-(a.b.d)\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertIsNone(result[0][1]._query)
            self.assertIsNone(result[0][1]._transform)
            self.assertEqual(len(result[0][1]._actions), 2)

    def test_multi_action_single_line_rule(self):
            result = RP.parseString("a.rule:\n+(a.b.c), -(a.b.d)\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertIsNone(result[0][1]._query)
            self.assertIsNone(result[0][1]._transform)
            self.assertEqual(len(result[0][1]._actions), 2)

    @unittest.skip("numbers have been deprecated")
    def test_rule_with_query_transform_actions(self):
            result = RP.parseString("a.rule:\na.b.c?\n\n$x + 20\n\n+(a.b.c)\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0][1], Rule)
            self.assertIsNotNone(result[0][1]._query)
            self.assertIsNotNone(result[0][1]._transform)
            self.assertEqual(len(result[0][1]._actions), 1)

    def test_rule_simple_binding_expansion(self):
        bindings = { "x" : FP.parseString('a.b.c')[0] }
        result = RP.parseString("a.rule:\n$x?\n\nend")[0][1]
        expanded = result.expand_bindings(bindings)
        self.assertEqual(str(expanded),
                         "a.rule:\n\ta.b.c?\n\nend")

    @unittest.skip("numbers have been deprecated")
    def test_rule_binding_expansion(self):
        bindings = { "x" : FP.parseString('a.b.c')[0],
                     "y" : FP.parseString('d.e.f')[0],
                     "z" : FP.parseString('x.y.z')[0] }
        result = RP.parseString("a.$x:\n$y.b.$z?\n\n$x + 2\n\n+($x)\nend")[0][1]
        expanded = result.expand_bindings(bindings)
        self.assertEqual(str(expanded),
                         "a.a.b.c:\n\td.e.f.b.x.y.z?\n\n\t$x + 2\n\n\t+(a.b.c)\nend")

    def test_rule_tags(self):
            result = RP.parseString('a.test.rule:\n#blah, #bloo, #blee\n\na.b.c?\n\n+(a.b.c)\nend')[0][1]
            self.assertIsInstance(result, Rule)
            self.assertEqual(str(result._name), "a.test.rule")
            self.assertTrue(all(x in result._tags for x in ["blah","bloo","blee"]))

    @unittest.skip("numbers have been deprecated")
    def test_fact_str_equal(self):
            rules = [ "a.rule:\nend",
                      "a.rule:\n\ta.b.c?\n\nend",
                      "a.rule:\n\ta.b.c?\n\ta.b!d?\n\nend",
                      "a.different.rule:\n\ta.b.c?\n\n\t$x + 20\n\nend",
                      "a.rule:\n\ta.b.c?\n\n\t$x + 20 -> $y\n\nend",
                      "a.rule:\n\ta.b.c?\n\n\t$x * 10 -> $AB\n\n\t+(a.b.d)\nend",
                      "a.rule:\n\t#blah, #blee, #bloo\n\nend"]

            parsed = [RP.parseString(x)[0][1] for x in rules]
            zipped = zip(rules, parsed)
            for r,p in zipped:
                  self.assertEqual(r,str(p))


    @unittest.skip("numbers have been deprecated")
    def test_bdi_rule_parse(self):
        rulestr = """bdi.blah:
    #propose
    count!$x(< 10)?

    $x + 2 -> $y
    ~{} "Hello: {x}" -> $z

    @($z)
    +(count!$y)
end
        """
        result = RP.parseString(rulestr)[0]
        self.assertEqual(result[0], KBU.RULE_S)
        self.assertIsInstance(result[1], Rule)

if __name__ == "__main__":
      LOGLEVEL = logging.INFO
      logFileName = "log.Trie_Rule_Parser_Tests"
      logging.basicConfig(filename=logFileName, level=LOGLEVEL, filemode='w')
      console = logging.StreamHandler()
      console.setLevel(logging.WARN)
      logging.getLogger().addHandler(console)
      unittest.main()
      #reminder: user logging.getLogger().setLevel(logging.NOTSET) for log control