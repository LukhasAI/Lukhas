import unittest

from matriz.nodes.tags_node import TagRegistryNode


class TestTagRegistryNode(unittest.TestCase):
    def test_get_tag(self):
        node = TagRegistryNode()
        input_data = {
            "query": {
                "operation": "get_tag",
                "args": {"tag_name": "#TAG:core"},
            }
        }
        result = node.process(input_data)
        self.assertEqual(result["answer"]["name"], "#TAG:core")
        self.assertTrue(node.validate_output(result))

if __name__ == "__main__":
    unittest.main()
