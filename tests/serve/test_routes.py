import pytest
from fastapi.testclient import TestClient
import sys
from unittest.mock import MagicMock

from serve.main import app

client = TestClient(app)


class TestTierAuth:
    def test_tier_auth_valid_token(self):
        """
        Test the tier-auth endpoint with a valid token.
        """
        response = client.post("/tier-auth/", json={"token": "symbolic-tier-3"})
        assert response.status_code == 200
        assert response.json() == {
            "access_rights": ["dream_summary", "ethical_prompt"],
            "tier": 3,
        }

    def test_tier_auth_invalid_token(self):
        """
        Test the tier-auth endpoint with an invalid token.
        """
        response = client.post("/tier-auth/", json={"token": "invalid-token"})
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid token"}

    def test_tier_auth_missing_token(self):
        """
        Test the tier-auth endpoint with a missing token.
        """
        response = client.post("/tier-auth/", json={})
        assert response.status_code == 422  # Unprocessable Entity


class TestGlyphFeedback:
    def test_glyph_feedback_high_drift(self):
        """
        Test glyph feedback with high drift score.
        """
        response = client.post(
            "/glyph-feedback/",
            json={"driftScore": 0.6, "collapseHash": "some-hash"},
        )
        assert response.status_code == 200
        suggestions = response.json()["suggestions"]
        assert "High drift detected - consider simplifying symbol complexity" in suggestions
        assert "Reduce symbolic noise by filtering redundant elements" in suggestions
        assert "Apply Guardian drift correction protocols" in suggestions

    def test_glyph_feedback_moderate_drift(self):
        """
        Test glyph feedback with moderate drift score.
        """
        response = client.post(
            "/glyph-feedback/",
            json={"driftScore": 0.2, "collapseHash": "some-hash"},
        )
        assert response.status_code == 200
        suggestions = response.json()["suggestions"]
        assert "Moderate drift (score: 0.200) - fine-tune symbol alignment" in suggestions

    def test_glyph_feedback_low_drift(self):
        """
        Test glyph feedback with low drift score.
        """
        response = client.post(
            "/glyph-feedback/",
            json={"driftScore": 0.05, "collapseHash": "some-hash"},
        )
        assert response.status_code == 200
        suggestions = response.json()["suggestions"]
        assert "Drift within acceptable range - maintain current configuration" in suggestions
        assert "Symbolic stability achieved - ready for consciousness integration" in suggestions


class TestGenerateDream:
    def test_generate_dream_with_consciousness(self, mocker):
        """
        Test dream generation when ConsciousnessCore is available.
        """
        mocker.patch("serve.routes.compute_drift_score", return_value=0.1)
        mocker.patch("serve.routes.compute_affect_delta", return_value=0.2)

        mock_auto_consciousness = MagicMock()
        mock_consciousness_instance = MagicMock()
        mock_consciousness_instance.generate_dream_narrative.return_value = "A mocked dream"
        mock_auto_consciousness.ConsciousnessCore.return_value = (
            mock_consciousness_instance
        )

        mocker.patch.dict(
            sys.modules,
            {"consciousness.unified.auto_consciousness": mock_auto_consciousness},
        )

        response = client.post(
            "/generate-dream/", json={"symbols": ["test", "symbol"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["dream"] == "A mocked dream"
        assert data["driftScore"] == 0.1
        assert data["affect_delta"] == 0.2
        mock_consciousness_instance.generate_dream_narrative.assert_called_once()

    def test_generate_dream_fallback(self, mocker):
        """
        Test dream generation fallback when ConsciousnessCore is not available.
        """
        mocker.patch("serve.routes.compute_drift_score", return_value=0.1)
        mocker.patch("serve.routes.compute_affect_delta", return_value=0.2)
        mocker.patch.dict(
            sys.modules, {"consciousness.unified.auto_consciousness": None}
        )

        response = client.post(
            "/generate-dream/", json={"symbols": ["test", "symbol"]}
        )
        assert response.status_code == 200
        data = response.json()
        assert "In this peaceful dream, test and symbol merge into one" in data["dream"]
        assert data["driftScore"] == 0.1
        assert data["affect_delta"] == 0.2


class TestPluginLoad:
    def test_plugin_load_new_file(self, mocker):
        """
        Test plugin loading when the registry file does not exist.
        """
        mock_path_class = mocker.patch("pathlib.Path")
        mock_path_instance = mock_path_class.return_value
        mock_registry_file = mock_path_instance.__truediv__.return_value
        mock_registry_file.exists.return_value = False

        mock_open = mocker.mock_open()
        mocker.patch("builtins.open", mock_open)
        mock_json_dump = mocker.patch("json.dump")

        response = client.post("/plugin-load/", json={"symbols": ["plugin1"]})

        assert response.status_code == 200
        assert response.json()["status"] == "loaded and persisted"

        mock_path_instance.mkdir.assert_called_once_with(
            parents=True, exist_ok=True
        )
        mock_open.assert_called_once_with(mock_registry_file, "w")

        args, _ = mock_json_dump.call_args
        dumped_data = args[0]
        assert "plugin1" in dumped_data
        assert dumped_data["plugin1"]["status"] == "active"
        assert dumped_data["plugin1"]["load_count"] == 1

    def test_plugin_load_existing_file(self, mocker):
        """
        Test plugin loading when the registry file already exists.
        """
        mock_path_class = mocker.patch("pathlib.Path")
        mock_path_instance = mock_path_class.return_value
        mock_registry_file = mock_path_instance.__truediv__.return_value
        mock_registry_file.exists.return_value = True

        mocker.patch(
            "builtins.open",
            mocker.mock_open(read_data='{"plugin1": {"load_count": 1}}'),
        )
        mocker.patch("json.load", return_value={"plugin1": {"load_count": 1}})
        mock_json_dump = mocker.patch("json.dump")

        response = client.post(
            "/plugin-load/", json={"symbols": ["plugin1", "plugin2"]}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "loaded and persisted"

        args, _ = mock_json_dump.call_args
        dumped_data = args[0]
        assert dumped_data["plugin1"]["load_count"] == 2
        assert dumped_data["plugin2"]["load_count"] == 1


class TestMemoryDump:
    def test_memory_dump_success(self, mocker):
        """
        Test memory dump when the memory subsystem is available.
        """
        mock_fold_manager_module = MagicMock()
        mock_fold_manager_instance = MagicMock()
        mock_fold_manager_instance.get_recent_folds.return_value = [
            {"fold_id": "mock_fold_1", "content": "mock content"}
        ]
        mock_fold_manager_module.FoldManager.return_value = (
            mock_fold_manager_instance
        )
        mocker.patch.dict(
            sys.modules, {"memory.unified.fold_manager": mock_fold_manager_module}
        )

        mock_process_emotion = mocker.patch("lukhas.emotion.process_emotion")
        mock_process_emotion.return_value = {
            "valence": 0.6,
            "arousal": 0.5,
            "dominance": 0.5,
        }
        mocker.patch.dict("os.environ", {}, clear=True)

        response = client.get("/memory-dump/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["folds"]) == 1
        assert data["folds"][0]["id"] == "mock_fold_1"
        assert data["emotional_state"]["valence"] == 0.6
        mock_process_emotion.assert_called_once()

    def test_memory_dump_fallback(self, mocker):
        """
        Test memory dump fallback when the memory subsystem is not available.
        """
        mocker.patch.dict(sys.modules, {"memory.unified.fold_manager": None})

        response = client.get("/memory-dump/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["folds"]) == 3
        assert data["folds"][0]["id"] == "fold_001"
        assert data["emotional_state"]["status"] == "fallback_mode"
