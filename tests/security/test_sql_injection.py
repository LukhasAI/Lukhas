import datetime as dt
import os
import unittest
from unittest.mock import patch

from lukhas_website.lukhas.aka_qualia.memory_sql import SqlMemory
from sqlalchemy import create_engine


class TestSqlInjection(unittest.TestCase):
    def setUp(self):
        self.db_path = "./test.db"
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.memory = SqlMemory(engine=self.engine)

    def tearDown(self):
        os.remove(self.db_path)

    def test_save_scene_with_malicious_input(self):
        user_id = "user1"
        scene = {"subject": "' OR 1=1; --", "proto": {}, "risk": {}}
        glyphs = []
        policy = {}
        metrics = {}
        cfg_version = "1.0"

        scene_id = self.memory.save(user_id=user_id, scene=scene, glyphs=glyphs, policy=policy, metrics=metrics, cfg_version=cfg_version)

        retrieved_scene = self.memory.history(user_id=user_id, limit=1)[0]
        self.assertEqual(retrieved_scene["subject"], "' OR 1=1; --")

    def test_fetch_prev_scene_with_malicious_user_id(self):
        user_id = "' OR 1=1; --"
        result = self.memory.fetch_prev_scene(user_id=user_id)
        self.assertIsNone(result)

    def test_history_with_malicious_user_id(self):
        user_id = "' OR 1=1; --"
        result = self.memory.history(user_id=user_id)
        self.assertEqual(len(result), 0)

    def test_search_by_glyph_with_malicious_key(self):
        user_id = "user1"
        key = "' OR 1=1; --"
        result = self.memory.search_by_glyph(user_id=user_id, key=key)
        self.assertEqual(len(result), 0)

    def test_top_drift_with_malicious_user_id(self):
        user_id = "' OR 1=1; --"
        result = self.memory.top_drift(user_id=user_id)
        self.assertEqual(len(result), 0)

    def test_delete_user_with_malicious_user_id(self):
        user_id = "' OR 1=1; --"
        result = self.memory.delete_user(user_id=user_id)
        self.assertEqual(result, 0)

    def test_parameterized_queries_for_save(self):
        user_id = "user1"
        scene = {"subject": "normal subject", "proto": {}, "risk": {}}
        glyphs = [{"key": "glyph1"}]
        policy = {}
        metrics = {}
        cfg_version = "1.0"

        self.memory.save(user_id=user_id, scene=scene, glyphs=glyphs, policy=policy, metrics=metrics, cfg_version=cfg_version)

        retrieved_scene = self.memory.history(user_id=user_id, limit=1)[0]
        self.assertEqual(retrieved_scene["subject"], "normal subject")

    def test_input_sanitization_in_context(self):
        user_id = "user1"
        scene = {
            "proto": {},
            "risk": {},
            "context": {
                "safe_palette": "test",
                "unsafe_field": "malicious data"
            }
        }
        glyphs = []
        policy = {}
        metrics = {}
        cfg_version = "1.0"

        scene_id = self.memory.save(user_id=user_id, scene=scene, glyphs=glyphs, policy=policy, metrics=metrics, cfg_version=cfg_version)

        retrieved_scene = self.memory.history(user_id=user_id, limit=1)[0]
        self.assertNotIn("unsafe_field", retrieved_scene["context"])
        self.assertIn("safe_palette", retrieved_scene["context"])

    def test_orm_usage_prevents_raw_sql(self):
        with patch('sqlalchemy.orm.session.Session.execute') as mock_execute:
            self.memory.history(user_id="user1")
            for call in mock_execute.call_args_list:
                # The first argument to execute will be a SQLAlchemy construct, not a raw string.
                self.assertNotIsInstance(call.args[0], str)

    def test_save_scene_parameterization(self):
        user_id = "test_user"
        scene = {'proto': {}, 'risk': {}, 'subject': 'test_subject'}
        glyphs = [{'key': 'test_glyph'}]
        policy = {}
        metrics = {}
        cfg_version = "v1"
        self.memory.save(user_id=user_id, scene=scene, glyphs=glyphs, policy=policy, metrics=metrics, cfg_version=cfg_version)
        history = self.memory.history(user_id=user_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]['subject'], 'test_subject')

    def test_fetch_prev_scene_parameterization(self):
        result = self.memory.fetch_prev_scene(user_id="non_existent_user")
        self.assertIsNone(result)

    def test_history_parameterization(self):
        result = self.memory.history(user_id="non_existent_user")
        self.assertEqual(len(result), 0)

    def test_search_by_glyph_parameterization(self):
        result = self.memory.search_by_glyph(user_id="non_existent_user", key="non_existent_key")
        self.assertEqual(len(result), 0)

    def test_top_drift_parameterization(self):
        result = self.memory.top_drift(user_id="non_existent_user")
        self.assertEqual(len(result), 0)

    def test_delete_user_parameterization(self):
        result = self.memory.delete_user(user_id="non_existent_user")
        self.assertEqual(result, 0)

    def test_save_with_single_quotes_in_subject(self):
        user_id = "user_quotes"
        scene = {"subject": "subject with 'single' quotes", "proto": {}, "risk": {}}
        self.memory.save(user_id=user_id, scene=scene, glyphs=[], policy={}, metrics={}, cfg_version="1.0")
        retrieved_scene = self.memory.history(user_id=user_id)[0]
        self.assertEqual(retrieved_scene['subject'], "subject with 'single' quotes")

    def test_save_with_double_quotes_in_subject(self):
        user_id = "user_double_quotes"
        scene = {"subject": "subject with \"double\" quotes", "proto": {}, "risk": {}}
        self.memory.save(user_id=user_id, scene=scene, glyphs=[], policy={}, metrics={}, cfg_version="1.0")
        retrieved_scene = self.memory.history(user_id=user_id)[0]
        self.assertEqual(retrieved_scene['subject'], "subject with \"double\" quotes")

    def test_save_with_semicolon_in_subject(self):
        user_id = "user_semicolon"
        scene = {"subject": "subject with; semicolon", "proto": {}, "risk": {}}
        self.memory.save(user_id=user_id, scene=scene, glyphs=[], policy={}, metrics={}, cfg_version="1.0")
        retrieved_scene = self.memory.history(user_id=user_id)[0]
        self.assertEqual(retrieved_scene['subject'], "subject with; semicolon")

    def test_save_with_comment_in_subject(self):
        user_id = "user_comment"
        scene = {"subject": "subject with -- comment", "proto": {}, "risk": {}}
        self.memory.save(user_id=user_id, scene=scene, glyphs=[], policy={}, metrics={}, cfg_version="1.0")
        retrieved_scene = self.memory.history(user_id=user_id)[0]
        self.assertEqual(retrieved_scene['subject'], "subject with -- comment")

    def test_save_with_union_attack_in_subject(self):
        user_id = "user_union"
        scene = {"subject": "subject' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20 --", "proto": {}, "risk": {}}
        self.memory.save(user_id=user_id, scene=scene, glyphs=[], policy={}, metrics={}, cfg_version="1.0")
        retrieved_scene = self.memory.history(user_id=user_id)[0]
        self.assertEqual(retrieved_scene['subject'], "subject' UNION SELECT 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20 --")

    def test_save_with_or_attack_in_subject(self):
        user_id = "user_or"
        scene = {"subject": "' or '1'='1", "proto": {}, "risk": {}}
        self.memory.save(user_id=user_id, scene=scene, glyphs=[], policy={}, metrics={}, cfg_version="1.0")
        retrieved_scene = self.memory.history(user_id=user_id)[0]
        self.assertEqual(retrieved_scene['subject'], "' or '1'='1")

if __name__ == "__main__":
    unittest.main()
