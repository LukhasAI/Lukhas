# LUKHAS Federated Learning System
# Transferred from Lucas-Portfolio Pre-Final 2 (2025-05-13)
# Enhanced for LUKHAS architecture

import datetime
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Optional

from candidate.core.common import get_logger

# TAG:consciousness
# TAG:states
# TAG:neuroplastic
# TAG:colony


logger = get_logger(__name__)


class LukhasFederatedModel:
    """
    LUKHAS Federated Model - Privacy-preserving distributed learning model

    Represents a model that can be trained in a federated manner,
    preserving privacy by keeping user data local while enabling
    collective learning across the LUKHAS network.
    """

    def __init__(self, model_id: str, model_type: str, initial_parameters: Optional[dict] = None):
        self.model_id = model_id
        self.model_type = model_type
        self.parameters = initial_parameters or {}
        self.version = 1
        self.last_updated = datetime.datetime.now(timezone.utc)
        self.contribution_count = 0
        self.client_contributions = set()
        self.performance_metrics = {}
        self.lukhas_signature = f"LUKHAS_{model_id}_{datetime.datetime.now(timezone.utc).strftime('%Y%m%d')}"

    def update_with_gradients(self, gradients: dict, client_id: str, weight: float = 1.0):
        """
        Update model parameters with gradients from a client

        Args:
            gradients: Parameter gradients calculated by client
            client_id: Identifier for the contributing client
            weight: Weight to apply to this client's contribution
        """
        if not gradients:
            logger.warning(f"Empty gradients received from client {client_id}")
            return False

        # Apply weighted gradients to parameters
        for param_name, grad_value in gradients.items():
            if param_name in self.parameters:
                # Apply gradient with weight
                self.parameters[param_name] += weight * grad_value
            else:
                # Initialize new parameter
                self.parameters[param_name] = weight * grad_value

        # Update metadata
        self.version += 1
        self.last_updated = datetime.datetime.now(timezone.utc)
        self.contribution_count += 1
        self.client_contributions.add(client_id)

        logger.info(f"Model {self.model_id} updated to v{self.version} with contribution from {client_id}")
        return True

    def get_parameters(self, client_id: Optional[str] = None) -> dict:
        """
        Get model parameters, optionally customized for a specific client

        Args:
            client_id: Optional client identifier for personalization

        Returns:
            Dictionary of model parameters with LUKHAS metadata
        """
        return {
            "model_id": self.model_id,
            "model_type": self.model_type,
            "parameters": self.parameters.copy(),
            "version": self.version,
            "lukhas_signature": self.lukhas_signature,
            "last_updated": self.last_updated.isoformat(),
            "client_count": len(self.client_contributions),
        }

    def serialize(self) -> dict:
        """Serialize model for storage with LUKHAS metadata"""
        return {
            "model_id": self.model_id,
            "model_type": self.model_type,
            "parameters": self.parameters,
            "version": self.version,
            "last_updated": self.last_updated.isoformat(),
            "contribution_count": self.contribution_count,
            "client_contributions": list(self.client_contributions),
            "performance_metrics": self.performance_metrics,
            "lukhas_signature": self.lukhas_signature,
            "lukhas_transferred": True,
        }

    @classmethod
    def deserialize(cls, data: dict) -> "LukhasFederatedModel":
        """Create model from serialized data"""
        model = cls(
            model_id=data["model_id"],
            model_type=data["model_type"],
            initial_parameters=data["parameters"],
        )
        model.version = data["version"]
        model.last_updated = datetime.datetime.fromisoformat(data["last_updated"])
        model.contribution_count = data["contribution_count"]
        model.client_contributions = set(data["client_contributions"])
        model.performance_metrics = data.get("performance_metrics", {})
        model.lukhas_signature = data.get("lukhas_signature", model.lukhas_signature)
        return model


class LukhasFederatedLearningManager:
    """
    LUKHAS Federated Learning Manager

    Manages federated learning across multiple LUKHAS clients while preserving privacy.
    Enhanced with LUKHAS-specific features and security measures.
    """

    def __init__(self, storage_dir: Optional[str] = None):
        self.models = {}  # model_id -> LukhasFederatedModel
        self.client_models = defaultdict(set)  # client_id -> set(model_ids)
        self.aggregation_threshold = 3  # Min clients before aggregation (reduced for LUKHAS)
        self.storage_dir = storage_dir or os.path.join(os.getcwd(), "lukhas_federated_models")
        self.lukhas_metadata = {
            "system": "LUKHAS",
            "transferred_from": "Lucas-Portfolio Pre-Final 2",
            "transfer_date": datetime.datetime.now(timezone.utc).isoformat(),
            "enhanced_features": [
                "lukhas_signatures",
                "reduced_aggregation_threshold",
                "enhanced_logging",
            ],
        }

        # Create storage directory if it doesn't exist
        Path(self.storage_dir).mkdir(parents=True, exist_ok=True)
        self.load_models()

    def register_model(
        self, model_id: str, model_type: str, initial_parameters: Optional[dict] = None
    ) -> LukhasFederatedModel:
        """
        Register a new model for federated learning in LUKHAS

        Args:
            model_id: Unique identifier for the model
            model_type: Type of model (e.g., "preference", "adaptation", "cognitive", "voice", "identity")
            initial_parameters: Initial parameter values

        Returns:
            The created LUKHAS federated model
        """
        if model_id in self.models:
            logger.info(f"Model {model_id} already exists, returning existing model")
            return self.models[model_id]

        model = LukhasFederatedModel(model_id, model_type, initial_parameters)
        self.models[model_id] = model
        self.save_model(model)

        logger.info(f"Registered new LUKHAS federated model: {model_id} ({model_type})")
        return model

    def get_model(self, model_id: str, client_id: Optional[str] = None) -> Optional[dict]:
        """
        Get model parameters for a LUKHAS client

        Args:
            model_id: ID of the model to retrieve
            client_id: ID of the requesting LUKHAS client

        Returns:
            Model parameters dictionary or None if not found
        """
        if model_id not in self.models:
            logger.warning(f"Model {model_id} not found")
            return None

        model = self.models[model_id]
        if client_id:
            self.client_models[client_id].add(model_id)

        return model.get_parameters(client_id)

    def contribute_gradients(
        self,
        model_id: str,
        gradients: dict,
        client_id: str,
        performance_metrics: Optional[dict] = None,
    ) -> bool:
        """
        Accept gradient contribution from a LUKHAS client

        Args:
            model_id: ID of the model to update
            gradients: Gradient updates from client
            client_id: ID of the contributing client
            performance_metrics: Optional performance metrics

        Returns:
            True if contribution was successful
        """
        if model_id not in self.models:
            logger.error(f"Cannot contribute to unknown model {model_id}")
            return False

        model = self.models[model_id]

        # Calculate contribution weight based on client history
        weight = self._calculate_client_weight(client_id, model_id)

        success = model.update_with_gradients(gradients, client_id, weight)

        if success:
            # Update performance metrics if provided
            if performance_metrics:
                model.performance_metrics[client_id] = {
                    **performance_metrics,
                    "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
                }

            # Save updated model
            self.save_model(model)

            # Check if aggregation threshold is met
            if len(model.client_contributions) >= self.aggregation_threshold:
                self._trigger_aggregation(model_id)

        return success

    def _calculate_client_weight(self, client_id: str, model_id: str) -> float:
        """Calculate contribution weight for a client"""
        # Simple implementation - can be enhanced with reputation system
        base_weight = 1.0

        # Reduce weight for very frequent contributors to prevent domination
        model = self.models[model_id]
        client_contribution_ratio = model.contribution_count / max(len(model.client_contributions), 1)

        # Apply diminishing returns for frequent contributors
        if client_contribution_ratio > 2.0:
            base_weight *= 0.8
        elif client_contribution_ratio > 5.0:
            base_weight *= 0.6

        return base_weight

    def _trigger_aggregation(self, model_id: str):
        """Trigger model aggregation when threshold is met"""
        logger.info(f"Triggering aggregation for model {model_id}")
        # In a full implementation, this would perform sophisticated aggregation
        # For now, we log the event
        model = self.models[model_id]
        model.performance_metrics["last_aggregation"] = {
            "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
            "participant_count": len(model.client_contributions),
            "version": model.version,
        }

    def save_model(self, model: LukhasFederatedModel):
        """Save model to disk with LUKHAS formatting"""
        model_path = os.path.join(self.storage_dir, f"{model.model_id}.json")
        with open(model_path, "w") as f:
            json.dump(model.serialize(), f, indent=2)

    def load_models(self):
        """Load all models from storage"""
        if not os.path.exists(self.storage_dir):
            return

        for filename in os.listdir(self.storage_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.storage_dir, filename)) as f:
                        data = json.load(f)
                    model = LukhasFederatedModel.deserialize(data)
                    self.models[model.model_id] = model
                    logger.info(f"Loaded LUKHAS federated model: {model.model_id}")
                except Exception as e:
                    logger.error(f"Failed to load model from {filename}: {e}")

    def get_system_status(self) -> dict:
        """Get overall system status"""
        return {
            "lukhas_federated_learning": {
                "total_models": len(self.models),
                "active_clients": len(self.client_models),
                "aggregation_threshold": self.aggregation_threshold,
                "storage_dir": self.storage_dir,
                "metadata": self.lukhas_metadata,
            },
            "models": {
                model_id: {
                    "type": model.model_type,
                    "version": model.version,
                    "contributors": len(model.client_contributions),
                    "last_updated": model.last_updated.isoformat(),
                }
                for model_id, model in self.models.items()
            },
        }


# LUKHAS-specific federated learning types
LUKHAS_MODEL_TYPES = {
    "identity": "User identity and preferences",
    "voice": "Voice adaptation and cultural learning",
    "cognitive": "Core reasoning and decision making",
    "adaptation": "System adaptation to user behavior",
    "security": "Security and privacy preferences",
    "memory": "Memory organization and retrieval",
    "dream": "Dream processing and narrative generation",
}


def initialize_lukhas_federated_learning(
    storage_dir: Optional[str] = None,
) -> LukhasFederatedLearningManager:
    """
    Initialize LUKHAS federated learning system

    Args:
        storage_dir: Optional custom storage directory

    Returns:
        Configured LUKHAS federated learning manager
    """
    manager = LukhasFederatedLearningManager(storage_dir)

    # Register default LUKHAS models
    for model_type, description in LUKHAS_MODEL_TYPES.items():
        model_id = f"lukhas_{model_type}_model"
        manager.register_model(
            model_id=model_id,
            model_type=model_type,
            initial_parameters={
                "description": description,
                "lukhas_version": "1.0",
                "initialized": datetime.datetime.now(timezone.utc).isoformat(),
            },
        )

    logger.info("LUKHAS Federated Learning System initialized successfully")
    return manager
