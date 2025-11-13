import unittest

from matriz.nodes.endocrine_node import EndocrineNode


class TestEndocrineNode(unittest.TestCase):
    def test_trigger_stress(self):
        node = EndocrineNode()
        input_data = {
            "query": {
                "operation": "trigger_stress",
                "args": {"intensity": 0.7},
            }
        }
        result = node.process(input_data)
        self.assertEqual(result["answer"], "Stress response triggered")
        self.assertTrue(node.validate_output(result))

if __name__ == "__main__":
    unittest.main()
