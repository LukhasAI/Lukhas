
import unittest
import os
import sys
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path

# This is a hack to get the import to work.
sys.path.insert(0, os.path.abspath("./lukhas_website"))

from lukhas.core.common.config import (
    ModuleConfig,
    ConfigLoader,
    get_config_loader,
    get_config,
    get_global_config,
    get_setting,
)
from lukhas.core.common import config as config_module

# Sample YAML and JSON content for mocking
SAMPLE_YAML_CONFIG = """
enabled: true
version: "2.0.0"
settings:
  database:
    host: "localhost"
    port: 5432
  api:
    key: "yaml_api_key"
dependencies:
  - "core"
  - "common"
"""

SAMPLE_JSON_CONFIG = """
{
  "enabled": false,
  "version": "3.0.0",
  "settings": {
    "database": {
      "host": "remotehost",
      "port": 5433
    },
    "api": {
      "key": "json_api_key"
    }
  },
  "dependencies": ["web"]
}
"""

SAMPLE_GLOBAL_YAML = """
environment: "production"
debug: false
log_level: "WARNING"
database:
  url: "prod_db_url"
"""


class TestConfig(unittest.TestCase):
    def setUp(self):
        # Reset the global config loader instance before each test
        config_module._config_loader = None
        # Clear lru_cache for get_config
        get_config.cache_clear()
        # Backup environment variables
        self.environ_backup = os.environ.copy()

    def tearDown(self):
        # Restore environment variables
        os.environ.clear()
        os.environ.update(self.environ_backup)

    def test_module_config_get(self):
        mc = ModuleConfig(
            name="test", settings={"a": {"b": {"c": 1}}, "x": 2}
        )
        self.assertEqual(mc.get("a.b.c"), 1)
        self.assertEqual(mc.get("x"), 2)
        self.assertIsNone(mc.get("a.b.d"))
        self.assertEqual(mc.get("a.b.d", "default"), "default")

    def test_module_config_set(self):
        mc = ModuleConfig(name="test")
        mc.set("a.b.c", 1)
        self.assertEqual(mc.settings, {"a": {"b": {"c": 1}}})
        mc.set("a.b.d", 2)
        self.assertEqual(mc.settings["a"]["b"]["d"], 2)

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_YAML_CONFIG)
    def test_load_module_config_yaml(self, mock_file, mock_exists):
        mock_exists.return_value = True
        loader = ConfigLoader(root_path=Path("/fake/root"))
        config = loader.load_module_config("test_module")

        self.assertEqual(config.name, "test_module")
        self.assertTrue(config.enabled)
        self.assertEqual(config.version, "2.0.0")
        self.assertEqual(config.get("database.host"), "localhost")
        self.assertEqual(config.dependencies, ["core", "common"])

    @patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_JSON_CONFIG)
    def test_load_module_config_json(self, mock_file):
        with patch("pathlib.Path.exists", return_value=True):
            loader = ConfigLoader(root_path=Path("/fake/root"))
            config = loader.load_module_config("test_module_json")

            self.assertFalse(config.enabled)
            self.assertEqual(config.version, "3.0.0")
            self.assertEqual(config.get("database.port"), 5433)

    @patch("pathlib.Path.exists", return_value=False)
    def test_load_module_config_no_file(self, mock_exists):
        loader = ConfigLoader(root_path=Path("/fake/root"))
        config = loader.load_module_config("no_file_module")

        self.assertEqual(config.name, "no_file_module")
        self.assertTrue(config.enabled)
        self.assertEqual(config.version, "1.0.0")
        self.assertEqual(config.settings, {})

    @patch("pathlib.Path.exists", return_value=False)
    def test_env_overrides(self, mock_exists):
        os.environ["LUKHAS_TEST_MODULE_ENABLED"] = "false"
        os.environ["LUKHAS_TEST_MODULE_VERSION"] = '"4.0.0"'  # JSON-encoded string
        os.environ["LUKHAS_TEST_MODULE_DATABASE_HOST"] = '"override.host"'
        os.environ["LUKHAS_TEST_MODULE_API_KEY"] = "env_key"

        loader = ConfigLoader(root_path=Path("/fake/root"))
        config = loader.load_module_config("test_module")

        self.assertEqual(config.get("enabled"), False)
        self.assertEqual(config.get("version"), "4.0.0")
        self.assertEqual(config.get("database.host"), "override.host")
        self.assertEqual(config.get("api.key"), "env_key")


    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_GLOBAL_YAML)
    def test_load_global_config(self, mock_file, mock_exists):
        mock_exists.return_value = True
        os.environ["LUKHAS_ENV"] = "test_env"

        loader = ConfigLoader(root_path=Path("/fake/root"))
        config = loader.load_global_config()

        self.assertEqual(config["environment"], "test_env")  # Env var takes precedence
        self.assertFalse(config["debug"])
        self.assertEqual(config["log_level"], "WARNING")
        self.assertEqual(config["database"]["url"], "prod_db_url")

    def test_get_database_config(self):
        os.environ["POSTGRES_HOST"] = "db_host"
        os.environ["POSTGRES_PORT"] = "5439"
        loader = ConfigLoader()
        db_config = loader.get_database_config()
        self.assertEqual(db_config["host"], "db_host")
        self.assertEqual(db_config["port"], 5439)

    def test_get_redis_config(self):
        os.environ["REDIS_HOST"] = "redis_host"
        os.environ["REDIS_DB"] = "2"
        loader = ConfigLoader()
        redis_config = loader.get_redis_config()
        self.assertEqual(redis_config["host"], "redis_host")
        self.assertEqual(redis_config["db"], 2)

    def test_get_guardian_config(self):
        os.environ["GUARDIAN_ETHICS_LEVEL"] = "permissive"
        loader = ConfigLoader()
        guardian_config = loader.get_guardian_config()
        self.assertEqual(guardian_config["ethics_level"], "permissive")

    def test_get_config_loader_singleton(self):
        loader1 = get_config_loader()
        loader2 = get_config_loader()
        self.assertIs(loader1, loader2)

    @patch("lukhas.core.common.config.ConfigLoader.load_module_config")
    def test_get_config_cached(self, mock_load):
        mock_load.return_value = ModuleConfig(name="cached_module")

        # First call should trigger load
        config1 = get_config("cached_module")
        mock_load.assert_called_once_with("cached_module")

        # Second call should hit the cache
        mock_load.reset_mock()
        config2 = get_config("cached_module")
        mock_load.assert_not_called()
        self.assertIs(config1, config2)

    @patch("lukhas.core.common.config.ConfigLoader.load_global_config")
    def test_get_global_config_function(self, mock_load):
        mock_load.return_value = {"global": "value"}
        config = get_global_config()
        self.assertEqual(config, {"global": "value"})

    @patch("lukhas.core.common.config.get_config")
    @patch("lukhas.core.common.config.get_global_config")
    def test_get_setting(self, mock_global_config, mock_module_config):
        # Test getting from global config
        mock_global_config.return_value = {"a": {"b": 1}}
        self.assertEqual(get_setting("a.b"), 1)

        # Test getting from module config
        mock_module = MagicMock()
        mock_module.get.return_value = "module_value"
        mock_module_config.return_value = mock_module
        self.assertEqual(get_setting("x.y", module="test_mod"), "module_value")
        mock_module.get.assert_called_once_with("x.y", None)

        # Test default value
        mock_global_config.return_value = {}
        self.assertEqual(get_setting("non.existent", "default"), "default")

    def test_find_project_root(self):
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "a" / "b"
            deep_path = project_root / "c"
            deep_path.mkdir(parents=True)
            (project_root / "lukhas_config.yaml").touch()

            with patch("pathlib.Path.cwd", return_value=deep_path):
                loader = ConfigLoader()
                self.assertEqual(loader.root_path, project_root)

    @patch("pathlib.Path.exists", return_value=True)
    def test_load_env(self, mock_exists):
        m = mock_open(read_data="KEY=VALUE\n#COMMENT\nINVALID_LINE")
        with patch("builtins.open", m):
            loader = ConfigLoader()
            loader.load_env()
            self.assertEqual(os.environ.get("KEY"), "VALUE")
            self.assertIsNone(os.environ.get("#COMMENT"))
            self.assertIsNone(os.environ.get("INVALID_LINE"))


if __name__ == "__main__":
    unittest.main()
