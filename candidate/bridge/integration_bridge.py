# --- LUKHΛS AI Standard Header ---
# File: integration_bridge.py
# Path: integration/framework/integration_bridge.py
# Project: LUKHΛS AI Model Integration Framework
# Created: 2023-09-15 (Approx. by LUKHΛS Team)
# Modified: 2024-07-27
# Version: 1.1
# License: Proprietary - LUKHΛS AI Use Only
# Contact: support@lukhas.ai
# Description: This module defines the IntegrationBridge and PluginModuleAdapter,
#              which are crucial for bridging the LUKHΛS plugin system with its
#              core modular framework. It enables seamless discovery, loading,
#              registration, and communication with plugins as if they were native modules.
# --- End Standard Header ---

# ΛTAGS: [Framework, Integration, PluginManagement, Adapter, Bridge, CoreRegistry, ΛTRACE_DONE]
# ΛNOTE: This bridge is a key component for LUKHΛS extensibility via plugins.
#        It relies on `plugin_base`, `plugin_loader`, `BaseLucasModule`, and `core_registry`.
#        Ensure these dependencies are correctly structured and importable.
#        The `SymbolicLogger` is being phased out in favor of `structlog`.

import asyncio
from datetime import (
    datetime,  # For consistent timestamping if needed
    timezone,
)
from pathlib import Path
from typing import Any, Optional

# Third-Party Imports
import structlog

# Initialize structlog logger for this module
log = structlog.get_logger(__name__)

# --- LUKHΛS System Imports (Fixed: Removed sys.path modifications) ---
# Fixed: Converted fragile sys.path modifications to robust absolute imports with fallback chains
LUKHAS_FRAMEWORK_COMPONENTS_AVAILABLE = False
try:
    # Try candidate lane first
    from candidate.bridge.plugin_base import LucasPlugin, LucasPluginManifest
    from candidate.bridge.plugin_loader import PluginLoader
    from candidate.core.registry import core_registry
    from candidate.core.utils.base_module import BaseLucasModule

    LUKHAS_FRAMEWORK_COMPONENTS_AVAILABLE = True
    log.info("LUKHΛS framework components imported successfully from candidate lane.")
except ImportError:
    try:
        # Fallback to production lane
        from lukhas.bridge.plugin_base import LucasPlugin, LucasPluginManifest
        from lukhas.bridge.plugin_loader import PluginLoader
        from lukhas.core.registry import core_registry
        from lukhas.core.utils.base_module import BaseLucasModule

        LUKHAS_FRAMEWORK_COMPONENTS_AVAILABLE = True
        log.info("LUKHΛS framework components imported successfully from production lane.")
    except ImportError:
        try:
            # Final fallback to relative imports for existing installations
            from .plugin_base import LucasPlugin, LucasPluginManifest
            from .plugin_loader import PluginLoader

            # Try to import core components from common locations
            try:
                from candidate.core.registry import core_registry
                from candidate.core.utils.base_module import BaseLucasModule
            except ImportError:
                from lukhas.core.registry import core_registry
                from lukhas.core.utils.base_module import BaseLucasModule

            LUKHAS_FRAMEWORK_COMPONENTS_AVAILABLE = True
            log.info("LUKHΛS framework components imported successfully via relative imports.")
        except ImportError as e:
            log.error(
                "Failed to import LUKHΛS framework components for IntegrationBridge. Fallbacks/Mocks might be used or errors may occur.",
                error_message=str(e),
                missing_dependencies_note="Ensure 'plugin_base.py', 'plugin_loader.py' are in the same package, and the 'lukhas' package (common.base_module, core.registry) is installed or in PYTHONPATH.",
            )
            LUKHAS_FRAMEWORK_COMPONENTS_AVAILABLE = False

if not LUKHAS_FRAMEWORK_COMPONENTS_AVAILABLE:
    # Define fallbacks if necessary for the script to parse, though
    # functionality will be broken.

    class BaseLucasModule:
        def __init__(self, *args, **kwargs):
            self.is_running = False
            self.log = log.bind(module_type="BaseLucasModule_Fallback")

        async def startup(self):
            self.is_running = True

        async def shutdown(self):
            self.is_running = False

        async def get_health_status(self):
            return {"status": "unknown_fallback"}

    class LucasPlugin:
        pass

    class LucasPluginManifest:
        def __init__(
            self,
            name="fallback_manifest",
            version="0.0",
            description="",
            author="",
            config=None,
            capabilities=None,
        ):
            self.name = name
            self.version = version
            self.description = description
            self.author = author
            self.config = config or {}
            self.capabilities = capabilities or []

    class PluginLoader:
        async def load_plugins(self, directory):
            log.error("PluginLoader fallback: cannot load plugins.")
            return {}

    class CoreRegistryMock:
        async def register(self, name, instance, version, module_type):
            log.warning(f"CoreRegistryMock: Registering {name}")
            return True

        async def unregister(self, name):
            log.warning(f"CoreRegistryMock: Unregistering {name}")
            return True

    core_registry = CoreRegistryMock()

# ΛTIER_CONFIG_START
# Tier mapping for LUKHΛS ID Service (Conceptual)
# {
#   "module": "integration.framework.integration_bridge",
#   "class_PluginModuleAdapter": {
#     "default_tier": 1,
#     "methods": {
#       "__init__": 0, "startup": 1, "shutdown": 1,
#       "get_health_status": 0, "process_symbolic_input": 1
#     }
#   },
#   "class_IntegrationBridge": {
#     "default_tier": 2, // Core system component
#     "methods": {
#       "__init__": 0,
#       "load_plugins_as_modules": 2, "unload_plugin_module": 2,
#       "get_plugin_module_status": 1, "send_to_plugin": 1,
#       "broadcast_to_plugins": 1, "get_plugins_by_capability": 1,
#       "route_to_capable_plugin": 1
#     }
#   },
#   "variables": {
#       "integration_bridge": 0 // Global instance, access controlled by its methods
#   }
# }
# ΛTIER_CONFIG_END


def lukhas_tier_required(level: int):  # Placeholder
    def decorator(func):
        func._lukhas_tier = level
        return func

    return decorator


@lukhas_tier_required(1)
class PluginModuleAdapter(BaseLucasModule):
    """
    Adapts a LUKHΛS Plugin (LucasPlugin) to conform to the BaseLucasModule interface.
    This allows plugins to be registered and managed within the LUKHΛS core module registry
    and participate in the system's lifecycle and communication patterns.
    """

    def __init__(self, plugin: LucasPlugin, manifest: LucasPluginManifest):
        """
        Initializes the adapter.
        Args:
            plugin: The plugin instance to adapt.
            manifest: The manifest data associated with the plugin.
        """
        super().__init__()  # Initializes self.log via BaseLucasModule if it uses structlog
        self.plugin = plugin
        self.manifest = manifest
        # If BaseLucasModule doesn't init self.log, or uses SymbolicLogger:
        # self.log = log.bind(adapter_for_plugin=manifest.name, plugin_version=manifest.version)
        # Ensure self.log is structlog-compatible
        if not hasattr(self, "log") or not hasattr(self.log, "bind"):  # Basic check
            self.log = log.bind(
                adapter_for_plugin=manifest.name,
                plugin_version=manifest.version,
            )

        self.config: dict[str, Any] = {
            "name": manifest.name,
            "version": manifest.version,
            "description": manifest.description,
            "author": manifest.author,
            "plugin_specific_config": manifest.config,  # Original plugin config
            "capabilities": manifest.capabilities,
            "adapter_class": self.__class__.__name__,
        }
        self.log.info("PluginModuleAdapter initialized.", plugin_name=self.manifest.name)

    @lukhas_tier_required(1)
    async def startup(self) -> None:
        """Starts the adapted plugin, calling its 'initialize' method if present."""
        self.log.info(f"Starting plugin '{self.manifest.name}' as a LUKHΛS module.")
        try:
            if hasattr(self.plugin, "initialize") and asyncio.iscoroutinefunction(self.plugin.initialize):
                await self.plugin.initialize()
            elif hasattr(self.plugin, "initialize"):
                self.plugin.initialize()  # For non-async initialize

            self.is_running = True  # Assuming BaseLucasModule has this attribute
            self.log.info(
                f"Plugin '{self.manifest.name}' started successfully.",
                plugin_name=self.manifest.name,
            )
        except Exception as e:
            self.log.error(
                f"Failed to start plugin '{self.manifest.name}'.",
                error_message=str(e),
                plugin_name=self.manifest.name,
                exc_info=True,
            )
            self.is_running = False
            raise  # Re-raise to indicate startup failure

    @lukhas_tier_required(1)
    async def shutdown(self) -> None:
        """Shuts down the adapted plugin, calling its 'cleanup' method if present."""
        self.log.info(
            f"Shutting down plugin '{self.manifest.name}'.",
            plugin_name=self.manifest.name,
        )
        try:
            if hasattr(self.plugin, "cleanup") and asyncio.iscoroutinefunction(self.plugin.cleanup):
                await self.plugin.cleanup()
            elif hasattr(self.plugin, "cleanup"):
                self.plugin.cleanup()  # For non-async cleanup

            self.is_running = False
            self.log.info(
                f"Plugin '{self.manifest.name}' shutdown successfully.",
                plugin_name=self.manifest.name,
            )
        except Exception as e:
            self.log.error(
                f"Failed to shutdown plugin '{self.manifest.name}'.",
                error_message=str(e),
                plugin_name=self.manifest.name,
                exc_info=True,
            )
            # Should not re-raise during shutdown unless critical

    @lukhas_tier_required(0)
    async def get_health_status(self) -> dict[str, Any]:
        """
        Retrieves the health status of the adapted plugin.
        Uses the plugin's 'get_health' method if available, otherwise provides a default status.
        """
        self.log.debug("Fetching health status.", plugin_name=self.manifest.name)
        try:
            plugin_health: dict[str, Any] = {}
            if hasattr(self.plugin, "get_health"):
                if asyncio.iscoroutinefunction(self.plugin.get_health):
                    plugin_health = await self.plugin.get_health()
                else:
                    plugin_health = self.plugin.get_health()  # type: ignore

            base_status = "healthy" if plugin_health.get("status") == "ok" else "unhealthy"
            if not plugin_health:  # If get_health doesn't exist or returns empty
                base_status = "healthy" if self.is_running else "stopped"

            return {
                "status": base_status,
                "details": plugin_health or "No detailed health from plugin.",
                "plugin_name": self.manifest.name,
                "plugin_version": self.manifest.version,
                "capabilities": self.manifest.capabilities,
                "is_adapter_running": self.is_running,  # From BaseLucasModule
                "timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            self.log.error(
                "Error getting plugin health status.",
                plugin_name=self.manifest.name,
                error_message=str(e),
                exc_info=True,
            )
            return {
                "status": "error",
                "error_message": str(e),
                "plugin_name": self.manifest.name,
                "timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
            }

    @lukhas_tier_required(1)
    async def process_symbolic_input(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Processes symbolic input by routing it to the plugin's 'process_symbolic' or 'process' method.
        Args:
            input_data: The symbolic data to be processed.
        Returns:
            A dictionary containing the processing status and result.
        """
        self.log.debug(
            "Processing symbolic input via plugin.",
            plugin_name=self.manifest.name,
            input_keys=list(input_data.keys()),
        )
        try:
            processing_method_name: Optional[str] = None
            if hasattr(self.plugin, "process_symbolic"):
                processing_method_name = "process_symbolic"
            elif hasattr(self.plugin, "process"):  # Fallback to generic process
                processing_method_name = "process"

            if processing_method_name:
                method_to_call = getattr(self.plugin, processing_method_name)
                if asyncio.iscoroutinefunction(method_to_call):
                    result = await method_to_call(input_data)
                else:
                    result = method_to_call(input_data)

                self.log.info(
                    "Symbolic input processed by plugin.",
                    plugin_name=self.manifest.name,
                    method_used=processing_method_name,
                )
                return {
                    "status": "success",
                    "result_payload": result,
                    "processed_by_plugin": self.manifest.name,
                    "processing_method": processing_method_name,
                    "timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
                }
            else:
                self.log.warning(
                    "Plugin does not support 'process_symbolic' or 'process' methods.",
                    plugin_name=self.manifest.name,
                )
                return {
                    "status": "error",
                    "error_message": f"Plugin '{self.manifest.name}' does not have a compatible processing method.",
                    "timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
                }
        except Exception as e:
            self.log.error(
                "Plugin processing failed.",
                plugin_name=self.manifest.name,
                error_message=str(e),
                exc_info=True,
            )
            return {
                "status": "error",
                "error_message": str(e),
                "timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
            }


@lukhas_tier_required(2)
class IntegrationBridge:
    """
    The IntegrationBridge facilitates the discovery, loading, and management of LUKHΛS plugins.
    It adapts plugins into standard LUKHΛS modules and registers them with the core_registry,
    allowing seamless interaction between plugins and the core system.
    """

    def __init__(self):
        self.plugin_loader = PluginLoader()
        self.log = log.bind(bridge_component="IntegrationBridge")
        self.plugin_adapters: dict[str, PluginModuleAdapter] = {}
        self.log.info("IntegrationBridge initialized.")

    @lukhas_tier_required(2)
    async def load_plugins_as_modules(self, plugins_directory_path: Optional[str] = None) -> dict[str, bool]:
        """
        Loads all plugins from the specified directory (or a default location),
        adapts them, and registers them as modules with the core_registry.
        Args:
            plugins_directory_path: Path to the directory containing plugins.
                                   Defaults to '../../plugins' relative to this file's directory.
        Returns:
            A dictionary mapping plugin names to their registration success (True/False).
        """
        if plugins_directory_path is None:
            # Default plugins directory: <current_project_root>/plugins
            # This assumes integration/framework/ is two levels down from project root.
            default_path = Path(__file__).resolve().parent.parent.parent / "plugins"
            plugins_directory_path = str(default_path)
            self.log.debug(f"Plugins directory not specified, using default: {plugins_directory_path}")

        self.log.info(f"Loading plugins from directory: {plugins_directory_path}")
        registration_results: dict[str, bool] = {}

        try:
            loaded_plugins_map = await self.plugin_loader.load_plugins(plugins_directory_path)
            self.log.info(
                f"PluginLoader found {len(loaded_plugins_map)} potential plugins.",
                count=len(loaded_plugins_map),
            )

            for plugin_name, (
                plugin_instance,
                manifest,
            ) in loaded_plugins_map.items():
                self.log.debug(
                    f"Processing loaded plugin: {plugin_name}",
                    version=manifest.version,
                )
                try:
                    adapter = PluginModuleAdapter(plugin_instance, manifest)
                    module_registry_id = f"plugin::{plugin_name}"  # Standardized ID

                    registration_successful = await core_registry.register(
                        name=module_registry_id,
                        instance=adapter,
                        version=manifest.version,
                        module_type="plugin_adapted",  # Clearer type
                    )

                    if registration_successful:
                        self.plugin_adapters[plugin_name] = (
                            adapter  # Store by original plugin name for bridge's internal use
                        )
                        registration_results[plugin_name] = True
                        self.log.info(
                            f"Plugin '{plugin_name}' (version {manifest.version}) registered successfully as module '{module_registry_id}'."
                        )
                        # Attempt to startup the adapted plugin module
                        await adapter.startup()
                    else:
                        registration_results[plugin_name] = False
                        self.log.error(
                            f"Failed to register plugin '{plugin_name}' as module '{module_registry_id}'. Registration returned false."
                        )
                except Exception as e_adapter:  # More specific exception handling
                    registration_results[plugin_name] = False
                    self.log.error(
                        f"Error adapting or registering plugin '{plugin_name}'.",
                        error_message=str(e_adapter),
                        exc_info=True,
                    )

            self.log.info(
                "Plugin loading and registration process complete.",
                successful_registrations=sum(registration_results.values()),
                total_attempted=len(registration_results),
            )
            return registration_results
        except Exception as e_loader:
            self.log.error(
                "Failed during plugin loading phase.",
                error_message=str(e_loader),
                directory_path=plugins_directory_path,
                exc_info=True,
            )
            return registration_results  # Return any partial results if applicable

    @lukhas_tier_required(2)
    async def unload_plugin_module(self, plugin_name: str) -> bool:
        """
        Unloads a specified plugin module. This involves shutting down the plugin
        and unregistering it from the core_registry.
        Args:
            plugin_name: The name of the plugin to unload.
        Returns:
            True if unloading was successful, False otherwise.
        """
        self.log.info(f"Attempting to unload plugin module: {plugin_name}")
        module_registry_id = f"plugin::{plugin_name}"
        adapter_to_unload = self.plugin_adapters.get(plugin_name)

        if not adapter_to_unload:
            self.log.warning(
                f"Plugin '{plugin_name}' not found in active adapters. Cannot unload.",
                target_plugin_name=plugin_name,
            )
            return False
        try:
            await adapter_to_unload.shutdown()  # Gracefully shutdown the plugin first

            unregistration_successful = await core_registry.unregister(module_registry_id)
            if unregistration_successful:
                del self.plugin_adapters[plugin_name]
                self.log.info(
                    f"Plugin '{plugin_name}' (module '{module_registry_id}') unloaded and unregistered successfully."
                )
                return True
            else:
                self.log.error(
                    f"Failed to unregister module '{module_registry_id}' for plugin '{plugin_name}'. It might still be in adapters list if shutdown failed before unregister.",
                    target_plugin_name=plugin_name,
                )
                # Consider if adapter should be removed from self.plugin_adapters even
                # if unregister fails
                return False
        except Exception as e:
            self.log.error(
                f"Failed to unload plugin '{plugin_name}'.",
                error_message=str(e),
                target_plugin_name=plugin_name,
                exc_info=True,
            )
            return False

    @lukhas_tier_required(1)
    async def get_plugin_module_status(self) -> dict[str, dict[str, Any]]:
        """
        Retrieves the status of all currently loaded and adapted plugin modules.
        Returns:
            A dictionary mapping plugin names to their status details.
        """
        self.log.debug("Fetching status for all plugin modules.")
        statuses: dict[str, dict[str, Any]] = {}
        for plugin_name, adapter in self.plugin_adapters.items():
            try:
                health_details = await adapter.get_health_status()
                statuses[plugin_name] = {
                    "health_report": health_details,
                    "manifest_summary": {
                        "name": adapter.manifest.name,
                        "version": adapter.manifest.version,
                        "description": adapter.manifest.description,
                        "capabilities": adapter.manifest.capabilities,
                    },
                    "is_adapter_marked_running": adapter.is_running,  # From BaseLucasModule state
                    "module_registry_id": f"plugin::{plugin_name}",
                }
            except Exception as e:
                self.log.error(
                    "Error getting status for plugin.",
                    plugin_name=plugin_name,
                    error_message=str(e),
                    exc_info=True,
                )
                statuses[plugin_name] = {
                    "error_message": f"Failed to retrieve status: {e!s}",
                    "is_adapter_marked_running": (adapter.is_running if adapter else "unknown"),
                    "timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
                }
        return statuses

    @lukhas_tier_required(1)
    async def send_to_plugin(self, plugin_name: str, method_name: str, *args: Any, **kwargs: Any) -> dict[str, Any]:
        """
        Sends a method call to a specific, named plugin.
        Args:
            plugin_name: The name of the target plugin.
            method_name: The name of the method to call on the plugin.
            *args: Positional arguments for the plugin method.
            **kwargs: Keyword arguments for the plugin method.
        Returns:
            A dictionary with the status and result of the method call.
        """
        self.log.debug(
            f"Sending method '{method_name}' to plugin '{plugin_name}'.",
            target_plugin=plugin_name,
            method=method_name,
            args_count=len(args),
            kwargs_keys=list(kwargs.keys()),
        )
        adapter = self.plugin_adapters.get(plugin_name)
        if not adapter:
            self.log.warning(
                "Target plugin for send_to_plugin not found.",
                target_plugin_name=plugin_name,
                method_to_call=method_name,
            )
            return {
                "status": "error",
                "error_message": f"Plugin '{plugin_name}' not found or not loaded.",
            }

        try:
            plugin_instance = adapter.plugin
            if hasattr(plugin_instance, method_name):
                method_to_execute = getattr(plugin_instance, method_name)
                if asyncio.iscoroutinefunction(method_to_execute):
                    result_payload = await method_to_execute(*args, **kwargs)
                else:
                    result_payload = method_to_execute(*args, **kwargs)

                self.log.debug(
                    f"Successfully called method '{method_name}' on plugin '{plugin_name}'.",
                    target_plugin=plugin_name,
                    method=method_name,
                )
                return {
                    "status": "success",
                    "result_payload": result_payload,
                    "timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
                }
            else:
                self.log.warning(
                    f"Method '{method_name}' not found on plugin '{plugin_name}'.",
                    target_plugin=plugin_name,
                    method_name=method_name,
                )
                return {
                    "status": "error",
                    "error_message": f"Plugin '{plugin_name}' does not have method '{method_name}'.",
                    "timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
                }
        except Exception as e:
            self.log.error(
                f"Error calling method '{method_name}' on plugin '{plugin_name}'.",
                target_plugin=plugin_name,
                method_name=method_name,
                error_message=str(e),
                exc_info=True,
            )
            return {
                "status": "error",
                "error_message": str(e),
                "timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
            }

    @lukhas_tier_required(1)
    async def broadcast_to_plugins(self, method_name: str, *args: Any, **kwargs: Any) -> dict[str, dict[str, Any]]:
        """
        Broadcasts a method call to all currently loaded plugins.
        Args:
            method_name: The name of the method to call on each plugin.
            *args: Positional arguments for the plugin method.
            **kwargs: Keyword arguments for the plugin method.
        Returns:
            A dictionary mapping plugin names to their respective method call results.
        """
        self.log.info(
            f"Broadcasting method '{method_name}' to all plugins.",
            method_to_broadcast=method_name,
            num_adapters=len(self.plugin_adapters),
        )
        broadcast_results: dict[str, dict[str, Any]] = {}
        for plugin_name_key in list(
            self.plugin_adapters.keys()
        ):  # Iterate over a copy of keys if modification during iteration is possible
            broadcast_results[plugin_name_key] = await self.send_to_plugin(
                plugin_name_key, method_name, *args, **kwargs
            )
        return broadcast_results

    @lukhas_tier_required(1)
    async def get_plugins_by_capability(self, capability_name: str) -> list[str]:
        """
        Retrieves a list of plugin names that declare a specific capability in their manifest.
        Args:
            capability_name: The name of the capability to search for.
        Returns:
            A list of plugin names possessing the specified capability.
        """
        self.log.debug(f"Searching for plugins with capability: {capability_name}")
        plugins_with_capability: list[str] = []
        for p_name, p_adapter in self.plugin_adapters.items():
            if capability_name in p_adapter.manifest.capabilities:
                plugins_with_capability.append(p_name)
        self.log.debug(
            f"Found {len(plugins_with_capability)} plugins with capability '{capability_name}'.",
            found_plugins=plugins_with_capability,
        )
        return plugins_with_capability

    @lukhas_tier_required(1)
    async def route_to_capable_plugin(
        self, capability_name: str, method_name: str, *args: Any, **kwargs: Any
    ) -> dict[str, Any]:
        """
        Routes a request to the first available plugin that possesses the required capability
        and then calls the specified method on it.
        Args:
            capability_name: The required capability.
            method_name: The method to call on the capable plugin.
            *args: Positional arguments for the plugin method.
            **kwargs: Keyword arguments for the plugin method.
        Returns:
            A dictionary with the status, result, and details of the routed call.
        """
        self.log.debug(
            f"Routing request for capability '{capability_name}' to method '{method_name}'.",
            capability=capability_name,
            method=method_name,
        )
        capable_plugin_names = await self.get_plugins_by_capability(capability_name)

        if not capable_plugin_names:
            self.log.warning(
                f"No plugins found with capability '{capability_name}' for routing.",
                target_capability=capability_name,
            )
            return {
                "status": "error",
                "error_message": f"No plugins found with capability '{capability_name}'.",
                "timestamp_utc_iso": datetime.now(timezone.utc).isoformat(),
            }

        # Simple strategy: try the first capable plugin found.
        # More complex strategies (e.g., round-robin, load-based) could be
        # implemented here.
        selected_plugin_name = capable_plugin_names[0]
        self.log.info(
            f"Routing to plugin '{selected_plugin_name}' for capability '{capability_name}'.",
            selected_plugin=selected_plugin_name,
            capability=capability_name,
        )

        call_result = await self.send_to_plugin(selected_plugin_name, method_name, *args, **kwargs)

        # Enhance the result with routing information
        call_result["routed_to_plugin"] = selected_plugin_name
        call_result["requested_capability"] = capability_name
        return call_result


# Global integration bridge instance
# ΛNOTE: Global instances can sometimes complicate testing and dependency management.
#        Consider if this should be managed/accessed via a central service locator
#        or dependency injection in a larger application context.
integration_bridge = IntegrationBridge()
log.info("Global IntegrationBridge instance created and available as 'integration_bridge'.")

# --- LUKHΛS AI Standard Footer ---
# File Origin: LUKHΛS Integration Framework - Core Components
# Context: This bridge is fundamental for LUKHΛS's plugin architecture, enabling
#          dynamic extension of system capabilities.
# ACCESSED_BY: ['SystemOrchestrator', 'CoreServiceManager', 'PluginAwareModules'] # Conceptual
# MODIFIED_BY: ['FRAMEWORK_ARCHITECTS', 'INTEGRATION_SPECIALISTS', 'Jules_AI_Agent'] # Conceptual
# Tier Access: Varies by method (Refer to ΛTIER_CONFIG block and @lukhas_tier_required decorators)
# Related Components: ['plugin_base.py', 'plugin_loader.py', 'lukhas.core.registry.core_registry']
# CreationDate: 2023-09-15 (Approx.) | LastModifiedDate: 2024-07-27 | Version: 1.1
# --- End Standard Footer ---
