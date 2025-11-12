import os
import unittest
from unittest.mock import patch

import pytest
import yaml
from config.env import EnvironmentConfig, LUKHASConfig, get_config


class TestEnvironmentConfig(unittest.TestCase):
    def setUp(self):
        self.config = EnvironmentConfig()
        # Reset global config instance in env module
        from config import env
        env._config_instance = None

    def tearDown(self):
        if os.path.exists("test.yaml"):
            os.remove("test.yaml")

    def test_get_from_env(self):
        with patch.dict(os.environ, {"MY_VAR": "env_value"}):
            self.assertEqual(self.config.get("MY_VAR"), "env_value")

    def test_get_from_yaml(self):
        yaml_content = {"MY_VAR": "yaml_value"}
        with open("test.yaml", "w") as f:
            yaml.dump(yaml_content, f)
        config = EnvironmentConfig("test.yaml")
        self.assertEqual(config.get("MY_VAR"), "yaml_value")

    def test_env_overrides_yaml(self):
        yaml_content = {"MY_VAR": "yaml_value"}
        with open("test.yaml", "w") as f:
            yaml.dump(yaml_content, f)
        with patch.dict(os.environ, {"MY_VAR": "env_value"}):
            config = EnvironmentConfig("test.yaml")
            self.assertEqual(config.get("MY_VAR"), "env_value")

    def test_get_with_default(self):
        self.assertEqual(self.config.get("NON_EXISTENT", "default_value"), "default_value")

    def test_get_required_raises_error(self):
        with self.assertRaises(ValueError):
            self.config.get("REQUIRED_VAR", required=True)

    def test_get_required_with_empty_string(self):
        with patch.dict(os.environ, {"REQUIRED_VAR": ""}), self.assertRaises(ValueError):
            self.config.get("REQUIRED_VAR", required=True)

    def test_get_required_from_env(self):
        with patch.dict(os.environ, {"REQUIRED_VAR": "value"}):
            self.assertEqual(self.config.get("REQUIRED_VAR", required=True), "value")

    def test_get_required_from_yaml(self):
        yaml_content = {"REQUIRED_VAR": "yaml_value"}
        with open("test.yaml", "w") as f:
            yaml.dump(yaml_content, f)
        config = EnvironmentConfig("test.yaml")
        self.assertEqual(config.get("REQUIRED_VAR", required=True), "yaml_value")

    def test_get_bool_true_variations(self):
        for val in ["true", "1", "yes", "on"]:
            with patch.dict(os.environ, {"MY_BOOL": val}):
                self.assertTrue(self.config.get_bool("MY_BOOL"))

    def test_get_bool_false_variations(self):
        for val in ["false", "0", "no", "off", "any_other_string"]:
            with patch.dict(os.environ, {"MY_BOOL": val}):
                self.assertFalse(self.config.get_bool("MY_BOOL"))

    def test_get_bool_from_yaml(self):
        yaml_content = {"MY_BOOL": True}
        with open("test.yaml", "w") as f:
            yaml.dump(yaml_content, f)
        config = EnvironmentConfig("test.yaml")
        self.assertTrue(config.get_bool("MY_BOOL"))

    def test_get_int(self):
        with patch.dict(os.environ, {"MY_INT": "123"}):
            self.assertEqual(self.config.get_int("MY_INT"), 123)

    def test_get_int_with_default(self):
        self.assertEqual(self.config.get_int("NON_EXISTENT", 42), 42)

    def test_get_int_invalid_value_returns_default(self):
        with patch.dict(os.environ, {"MY_INT": "not-an-int"}):
            self.assertEqual(self.config.get_int("MY_INT", default=99), 99)

    def test_get_int_invalid_value_required_raises_error(self):
        with patch.dict(os.environ, {"MY_INT": "not-an-int"}):
            with self.assertRaises(ValueError):
                self.config.get_int("MY_INT", required=True)

    def test_get_float(self):
        with patch.dict(os.environ, {"MY_FLOAT": "123.45"}):
            self.assertEqual(self.config.get_float("MY_FLOAT"), 123.45)

    def test_get_float_invalid_value_required_raises_error(self):
        with patch.dict(os.environ, {"MY_FLOAT": "not-a-float"}):
            with self.assertRaises(ValueError):
                self.config.get_float("MY_FLOAT", required=True)

    def test_get_list(self):
        with patch.dict(os.environ, {"MY_LIST": "a,b, c"}):
            self.assertEqual(self.config.get_list("MY_LIST"), ["a", "b", "c"])

    def test_get_list_with_custom_separator(self):
        with patch.dict(os.environ, {"MY_LIST": "a; b; c"}):
            self.assertEqual(self.config.get_list("MY_LIST", separator=";"), ["a", "b", "c"])

    def test_get_list_with_empty_items(self):
        with patch.dict(os.environ, {"MY_LIST": "a,,b, ,c"}):
            self.assertEqual(self.config.get_list("MY_LIST"), ["a", "b", "c"])

    def test_validate_required_success(self):
        with patch.dict(os.environ, {"REQ1": "val1"}):
            self.config.get("REQ1", required=True)
            self.config.validate_required() # Should not raise

    def test_validate_required_failure(self):
        with patch.dict(os.environ, {"REQ1": "val1"}):
            self.config.get("REQ1", required=True) # Register the var
        # Now the variable is gone from the environment
        with self.assertRaises(ValueError) as cm:
            self.config.validate_required()
        self.assertIn("REQ1", str(cm.exception))

    def test_get_status(self):
        yaml_content = {"YAML_KEY": "val"}
        with open("test.yaml", "w") as f:
            yaml.dump(yaml_content, f)
        config = EnvironmentConfig("test.yaml")
        with patch.dict(os.environ, {"REQ": "val"}):
            config.get("REQ", required=True)
        config.get("OPT", default="def")
        status = config.get_status()
        self.assertEqual(status["required_vars"], 1)
        self.assertEqual(status["optional_vars"], 1)
        self.assertTrue(status["yaml_config_loaded"])
        self.assertEqual(status["yaml_keys"], ["YAML_KEY"])


class TestLUKHASConfig(unittest.TestCase):
    def setUp(self):
        # Reset the global config instance before each test
        from config import env
        env._config_instance = None
        self.config = get_config()
        # Clean up environment variables
        self.env_patcher = patch.dict(os.environ, clear=True)
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()

    @patch.dict(os.environ, {"ENVIRONMENT": "production", "OPENAI_API_KEY": "key", "LUKHAS_ID_SECRET": "a"*32, "JWT_SECRET": "b"*32, "ENCRYPTION_KEY": "c"*32})
    def test_production_validation_success(self):
        lukhas_config = LUKHASConfig(self.config)
        lukhas_config.validate()

    @patch.dict(os.environ, {"ENVIRONMENT": "production", "OPENAI_API_KEY": "", "LUKHAS_ID_SECRET": "a"*32, "JWT_SECRET": "b"*32, "ENCRYPTION_KEY": "c"*32})
    def test_production_validation_missing_openai_key(self):
        lukhas_config = LUKHASConfig(self.config)
        with self.assertRaises(ValueError):
            lukhas_config.validate()

    @patch.dict(os.environ, {"ENVIRONMENT": "production", "OPENAI_API_KEY": "key", "LUKHAS_ID_SECRET": "short", "JWT_SECRET": "b"*32, "ENCRYPTION_KEY": "c"*32})
    def test_production_validation_short_lukhas_id_secret(self):
        lukhas_config = LUKHASConfig(self.config)
        with self.assertRaisesRegex(ValueError, "LUKHAS_ID_SECRET must be at least 32 characters"):
            lukhas_config.validate()

    @patch.dict(os.environ, {"ENVIRONMENT": "production", "OPENAI_API_KEY": "key", "LUKHAS_ID_SECRET": "a"*32, "JWT_SECRET": "short", "ENCRYPTION_KEY": "c"*32})
    def test_production_validation_short_jwt_secret(self):
        lukhas_config = LUKHASConfig(self.config)
        with self.assertRaisesRegex(ValueError, "JWT_SECRET must be at least 32 characters"):
            lukhas_config.validate()

    @patch.dict(os.environ, {"ENVIRONMENT": "development", "LUKHAS_ID_SECRET": "a"*32, "JWT_SECRET": "b"*32, "ENCRYPTION_KEY": "c"*32})
    def test_development_validation_success(self):
        lukhas_config = LUKHASConfig(self.config)
        lukhas_config.validate() # Should not raise

    def test_debug_mode_in_dev(self):
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            lukhas_config = LUKHASConfig(self.config)
            self.assertTrue(lukhas_config.debug)

    def test_debug_mode_in_prod(self):
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            lukhas_config = LUKHASConfig(self.config)
            self.assertFalse(lukhas_config.debug)

    def test_log_level_in_dev(self):
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            lukhas_config = LUKHASConfig(self.config)
            self.assertEqual(lukhas_config.log_level, "DEBUG")

    def test_log_level_in_prod(self):
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            lukhas_config = LUKHASConfig(self.config)
            self.assertEqual(lukhas_config.log_level, "INFO")

    def test_database_url_default(self):
        lukhas_config = LUKHASConfig(self.config)
        self.assertEqual(lukhas_config.database_url, "sqlite:///db")

    def test_redis_url_custom(self):
        with patch.dict(os.environ, {"REDIS_URL": "redis://custom:1234/1"}):
            lukhas_config = LUKHASConfig(self.config)
            self.assertEqual(lukhas_config.redis_url, "redis://custom:1234/1")

    def test_api_rate_limit_default(self):
        lukhas_config = LUKHASConfig(self.config)
        self.assertEqual(lukhas_config.api_rate_limit_per_minute, 1000)

    def test_guardian_drift_threshold_custom(self):
        with patch.dict(os.environ, {"GUARDIAN_DRIFT_THRESHOLD": "0.5"}):
            lukhas_config = LUKHASConfig(self.config)
            self.assertEqual(lukhas_config.guardian_drift_threshold, 0.5)

    def test_api_vault_path_resolving(self):
        with patch.dict(os.environ, {"LUKHAS_API_VAULT_PATH": "my_vault"}):
            lukhas_config = LUKHASConfig(self.config)
            # Should resolve relative to repo root
            self.assertTrue(str(lukhas_config.api_vault_path).endswith("/my_vault"))
            self.assertTrue(lukhas_config.api_vault_path.is_absolute())
