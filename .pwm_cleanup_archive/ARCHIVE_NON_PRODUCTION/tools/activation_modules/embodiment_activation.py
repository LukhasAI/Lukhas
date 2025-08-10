"""
Auto-generated entity activation for embodiment system
Generated: 2025-07-30T18:33:00.551620
Total Classes: 1
Total Functions: 2
"""

import logging

logger = logging.getLogger(__name__)

# Entity definitions
EMBODIMENT_CLASS_ENTITIES = [
    ("body_state", "ProprioceptiveState"),
]

EMBODIMENT_FUNCTION_ENTITIES = [
    ("body_state", "to_dict"),
    ("body_state", "update_joint"),
]


class EmbodimentEntityActivator:
    """Activator for embodiment system entities"""

    def __init__(self, hub_instance):
        self.hub = hub_instance
        self.activated_count = 0
        self.failed_count = 0

    def activate_all(self):
        """Activate all embodiment entities"""
        logger.info("Starting embodiment entity activation...")

        # Activate classes
        self._activate_classes()

        # Activate functions
        self._activate_functions()

        logger.info(
            f"{system_name} activation complete: {self.activated_count} activated, {self.failed_count} failed"
        )

        return {
            "activated": self.activated_count,
            "failed": self.failed_count,
            "total": len(EMBODIMENT_CLASS_ENTITIES) + len(EMBODIMENT_FUNCTION_ENTITIES),
        }

    def _activate_classes(self):
        """Activate class entities"""
        for module_path, class_name in EMBODIMENT_CLASS_ENTITIES:
            try:
                # Build full module path
                if module_path.startswith("."):
                    full_path = f"{system_name}{module_path}"
                else:
                    full_path = f"{system_name}.{module_path}"

                # Import module
                module = __import__(full_path, fromlist=[class_name])
                cls = getattr(module, class_name)

                # Register with hub
                service_name = self._generate_service_name(class_name)

                # Try to instantiate if possible
                try:
                    instance = cls()
                    self.hub.register_service(service_name, instance)
                    logger.debug(f"Activated {class_name} as {service_name}")
                except:
                    # Register class if can't instantiate
                    self.hub.register_service(f"{service_name}_class", cls)
                    logger.debug(f"Registered {class_name} class")

                self.activated_count += 1

            except Exception as e:
                logger.warning(
                    f"Failed to activate {class_name} from {module_path}: {e}"
                )
                self.failed_count += 1

    def _activate_functions(self):
        """Activate function entities"""
        for module_path, func_name in EMBODIMENT_FUNCTION_ENTITIES:
            try:
                # Build full module path
                if module_path.startswith("."):
                    full_path = f"{system_name}{module_path}"
                else:
                    full_path = f"{system_name}.{module_path}"

                # Import module
                module = __import__(full_path, fromlist=[func_name])
                func = getattr(module, func_name)

                # Register function
                service_name = f"{func_name}_func"
                self.hub.register_service(service_name, func)
                logger.debug(f"Activated function {func_name}")

                self.activated_count += 1

            except Exception as e:
                logger.warning(
                    f"Failed to activate function {func_name} from {module_path}: {e}"
                )
                self.failed_count += 1

    def _generate_service_name(self, class_name: str) -> str:
        """Generate consistent service names"""
        import re

        # Convert CamelCase to snake_case
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
        name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

        # Remove common suffixes
        for suffix in ["_manager", "_service", "_system", "_engine", "_handler"]:
            if name.endswith(suffix):
                name = name[: -len(suffix)]
                break

        return name


def get_embodiment_activator(hub_instance):
    """Factory function to create activator"""
    return EmbodimentEntityActivator(hub_instance)
