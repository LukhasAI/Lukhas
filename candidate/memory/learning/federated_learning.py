import json
import os
from datetime import datetime
from typing import Optional


class FederatedLearningManager:
    """
    Manages federated learning across distributed clients while preserving privacy.
    Handles model registration, gradient contributions, and model persistence.
    """

    def __init__(self, storage_path: str, timezone):
        self.storage_path = storage_path
        self.models = {}  # In-memory model cache
        self._ensure_storage_exists()

    def register_model(self, model_id: str, model_type: str, initial_weights: dict) -> None:
        """Register a new model for federated learning"""
        model_data = {
            "model_id": model_id,
            "model_type": model_type,
            "weights": initial_weights,
            "version": 1,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "contributors": set(),  # Track unique contributors
        }

        self.models[model_id] = model_data
        self._persist_model(model_id)

    def get_model(self, model_id: str, client_id: str) -> Optional[dict]:
        """Retrieve a model's current state"""
        if model_id not in self.models:
            self._load_model(model_id)  # Try loading from disk

        if model_id not in self.models:
            return None

        model = self.models[model_id]
        model["contributors"].add(client_id)  # Track model access
        return {
            "weights": model["weights"],
            "version": model["version"],
            "model_type": model["model_type"],
        }

    def contribute_gradients(
        self,
        model_id: str,
        client_id: str,
        gradients: dict,
        metrics: Optional[dict] = None,
    ) -> None:
        """Update model with client's gradient contributions"""
        if model_id not in self.models:
            return  # Model must be registered first

        model = self.models[model_id]
        model["contributors"].add(client_id)

        # Apply gradients - in practice would use proper gradient aggregation
        # Here we do a simple weighted update
        weights = model["weights"]
        for key, gradient in gradients.items():
            if key in weights:
                weights[key] = self._weighted_update(weights[key], gradient)

        model["version"] += 1
        model["last_updated"] = datetime.now(timezone.utc).isoformat()

        if metrics:
            model["metrics"] = metrics

        self._persist_model(model_id)

    def _weighted_update(self, current_value, gradient, learning_rate: float = 0.1):
        """Apply a weighted update to a value"""
        if isinstance(current_value, dict):
            return {k: self._weighted_update(v, gradient[k]) for k, v in current_value.items()}
        elif isinstance(current_value, (int, float)):
            return current_value + learning_rate * gradient
        return current_value

    def _ensure_storage_exists(self) -> None:
        """Ensure the storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)

    def _get_model_path(self, model_id: str) -> str:
        """Get the filesystem path for a model"""
        return os.path.join(self.storage_path, f"{model_id}.json")

    def _persist_model(self, model_id: str) -> None:
        """Save model state to disk"""
        model = self.models[model_id]
        model_path = self._get_model_path(model_id)

        # Convert set to list for JSON serialization
        model_data = dict(model)
        model_data["contributors"] = list(model["contributors"])

        with open(model_path, "w") as f:
            json.dump(model_data, f, indent=2)

    def _load_model(self, model_id: str) -> None:
        """Load model state from disk"""
        model_path = self._get_model_path(model_id)
        if not os.path.exists(model_path):
            return

        with open(model_path) as f:
            model_data = json.load(f)
            # Convert contributors back to set
            model_data["contributors"] = set(model_data["contributors"])
            self.models[model_id] = model_data
