import unittest
import logging
from test_context import pyRule
from pyRule.trie import RuleParser as RP
from pyRule.trie.Rule import Rule
from pyRule.trie.Query import Query

class Trie_Rule_Parser_Tests(unittest.TestCase):
      
      def setUp(self):
            return 1

      def tearDown(self):
            return 1

      #----------
      #use testcase snippets
      def test_init(self):
            self.assertIsNotNone(RP)

      def test_name_empty_rule_parse(self):
            result = RP.parseString(".a.rule:\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], Rule)
            self.assertEqual("".join([str(x) for x in result[0]._name]),
                             "||root.a.rule")

      def test_multi_empty_rules(self):
            result = RP.parseString(".a.rule:\nend\n\n.a.second.rule:\nend")
            self.assertEqual(len(result),2)
            self.assertTrue(all([isinstance(x,Rule) for x in result]))
      
      def test_rule_with_query(self):
            result = RP.parseString(".a.rule:\n.a.b.c?\n\nend")
            self.assertEqual(len(result),1)
            self.assertIsInstance(result[0], Rule)
            self.assertIsNotNone(result[0]._query)
            self.assertIsInstance(result[0]._query, Query)

      def test_rule_with_multi_clause_query(self):
            result = RP.parseString(".a.rule:\n.a.b.c?,\n.a.b.d?\n\nend")
            self.assertEqual(len(result),1)
            self.assertIsInstance(result[0], Rule)
            self.assertIsNotNone(result[0]._query)
            self.assertIsInstance(result[0]._query, Query)
            self.assertEqual(len(result[0]._query), 2)

      def test_rule_with_multi_clauses_in_one_line(self):
            result = RP.parseString(".a.rule:\n.a.b.c?, .a.b.d?\n\nend")
            self.assertEqual(len(result),1)
            self.assertIsInstance(result[0], Rule)
            self.assertIsNotNone(result[0]._query)
            self.assertIsInstance(result[0]._query, Query)
            self.assertEqual(len(result[0]._query), 2)
            
      def test_rule_with_binding_query(self):
            result = RP.parseString(".a.rule:\n.a.b.$x?\n\nend")
            self.assertEqual(len(result),1)
            self.assertIsInstance(result[0], Rule)
            self.assertIsNotNone(result[0]._query)
            self.assertIsInstance(result[0]._query, Query)
            self.assertEqual(len(result[0]._query), 1)

      def test_rule_with_transform(self):
            result = RP.parseString(".a.rule:\n$x + 20 -> $y\n\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], Rule)
            self.assertIsNone(result[0]._query)
            self.assertIsNotNone(result[0]._transform)

      def test_rule_with_multiple_transforms(self):
            result = RP.parseString(".a.rule:\n$x + 20 -> $y,\n$y - 20\n\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], Rule)
            self.assertIsNone(result[0]._query)
            self.assertIsNotNone(result[0]._transform)

      def test_rule_with_multiple_transforms_on_single_line(self):
            result = RP.parseString(".a.rule:\n$x + 20 -> $y,$y - 20\n\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], Rule)
            self.assertIsNone(result[0]._query)
            self.assertIsNotNone(result[0]._transform)

            
      def test_rule_with_actions(self):
            result = RP.parseString(".a.rule:\n+(.a.b.c)\n\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], Rule)
            self.assertIsNone(result[0]._query)
            self.assertIsNone(result[0]._transform)
            self.assertEqual(len(result[0]._actions), 1)

      def test_multi_action_rule(self):
            result = RP.parseString(".a.rule:\n+(.a.b.c),\n-(.a.b.d)\n\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], Rule)
            self.assertIsNone(result[0]._query)
            self.assertIsNone(result[0]._transform)
            self.assertEqual(len(result[0]._actions), 2)

      def test_multi_action_single_line_rule(self):
            result = RP.parseString(".a.rule:\n+(.a.b.c), -(.a.b.d)\n\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], Rule)
            self.assertIsNone(result[0]._query)
            self.assertIsNone(result[0]._transform)
            self.assertEqual(len(result[0]._actions), 2)

      def test_rule_with_query_transform_actions(self):
            result = RP.parseString(".a.rule:\n.a.b.c?\n\n$x + 20\n\n+(.a.b.c)\n\nend")
            self.assertEqual(len(result), 1)
            self.assertIsInstance(result[0], Rule)
            self.assertIsNotNone(result[0]._query)
            self.assertIsNotNone(result[0]._transform)
            self.assertEqual(len(result[0]._actions), 1)
            

if __name__ == "__main__":
      LOGLEVEL = logging.INFO
      logFileName = "log.Trie_Rule_Parser_Tests"
      logging.basicConfig(filename=logFileName, level=LOGLEVEL, filemode='w')
      console = logging.StreamHandler()
      console.setLevel(logging.WARN)
      logging.getLogger().addHandler(console)
      unittest.main()
      #reminder: user logging.getLogger().setLevel(logging.NOTSET) for log control
