import pytest
from pathlib import Path
import shutil

from candidate.core.glyph.api_manager import LUKHASAPIManager

@pytest.fixture
def temp_storage_path(tmp_path):
    """Create a temporary storage path for the API manager."""
    path = tmp_path / "api_vault"
    path.mkdir()
    yield path
    shutil.rmtree(path)

class TestLUKHASAPIManager:
    def test_init_with_storage_path(self, temp_storage_path):
        """
        Tests if the LUKHASAPIManager is initialized correctly with a storage path.
        """
        manager = LUKHASAPIManager(storage_path=temp_storage_path)
        assert manager.storage_path == temp_storage_path
        assert temp_storage_path.exists()

    def test_init_creates_directory(self, tmp_path):
        """
        Tests if the LUKHASAPIManager creates the storage directory if it doesn't exist.
        """
        new_path = tmp_path / "new_api_vault"
        assert not new_path.exists()

        manager = LUKHASAPIManager(storage_path=new_path)

        assert new_path.exists()
        assert manager.storage_path == new_path
        shutil.rmtree(new_path)
